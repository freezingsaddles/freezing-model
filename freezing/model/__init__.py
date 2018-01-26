import re
import warnings
import json
import inspect
from typing import Dict, Any, List

from alembic import command

import sqlalchemy as sa
from alembic.script import ScriptDirectory
from alembic.util import CommandError

from freezing.model.exc import DatabaseVersionError

from sqlalchemy import create_engine, Table
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.engine import Engine
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import Pool
from sqlalchemy.sql.expression import Executable, ClauseElement
from sqlalchemy.types import TypeDecorator, TEXT

from . import meta, migrationsutil
from .autolog import log

Base = declarative_base(metadata=meta.metadata)

# Global list of managed tables is populated from .orm module
MANAGED_TABLES = []


def register_managed_tables(tables:List[Table]):
    """
    Register an ORM Table object as something that should be managed (created/dropped).

    This is invoked by the orm module at import time.
    """
    MANAGED_TABLES.extend(tables)


def init_model(sqlalchemy_url:str, drop:bool=False, check_version:bool=True):
    """
    Initializes the tables and classes of the model using configured engine.

    :param sqlalchemy_url: The database URI.
    :param drop: Whether to drop the tables first.
    :param check_version: Whether to ensure that the database version is up-to-date.
    """
    engine = create_engine(sqlalchemy_url)

    sm = sessionmaker(autoflush=True, autocommit=False, bind=engine)
    meta.engine = engine
    meta.scoped_session = scoped_session(sm)

    alembic_cfg = migrationsutil.create_config(sqlalchemy_url=sqlalchemy_url)

    alembic_script = ScriptDirectory.from_config(alembic_cfg)

    # Check to see whether the database has already been created or not.
    # Based on this, we know whether we need to upgrade the database or mark the database
    # as the latest version.

    inspector = Inspector.from_engine(engine)

    db_objects_created = len(inspector.get_table_names()) > 1

    fresh_db = False

    if not db_objects_created:
        log.info("Database apears uninitialized, creating database tables")
        meta.metadata.create_all(engine, tables=MANAGED_TABLES, checkfirst=True)
        create_supplemental_db_objects(engine)
        fresh_db = True
    elif drop:
        log.info("Dropping database tables and re-creating.")
        drop_supplemental_db_objects(engine)
        meta.metadata.drop_all(engine, tables=MANAGED_TABLES, checkfirst=True)
        meta.metadata.create_all(engine, tables=MANAGED_TABLES)
        fresh_db = True

    if fresh_db:
        command.stamp(alembic_cfg, "head")
    else:
        if check_version:
            latest = alembic_script.get_current_head()
            installed = migrationsutil.get_database_version()
            try:
                alembic_script.get_revisions(installed)
            except CommandError:
                warnings.warn("Unknown db revision {} installed, ignoring db upgrade.".format(installed))
            else:
                if latest != installed:
                    log.info("Installed database ({0}) does not match latest available ({1}). (UPGRADING)".format(installed, latest), UserWarning)
                    command.upgrade(alembic_cfg, "head")
        else:
            log.info("Skipping database upgrade.")


class JSONEncodedText(TypeDecorator):
    """Represents an immutable structure as a json-encoded string.

    Usage::

        JSONEncodedText
    """

    impl = TEXT

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)

        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class CreateView(Executable, ClauseElement):
    def __init__(self, name, select):
        self.name = name
        self.select = select


@compiles(CreateView, 'mysql')
def visit_create_view(element, compiler, **kw):
    return "CREATE VIEW IF NOT EXISTS %s AS %s" % (
        element.name,
        compiler.process(element.select, literal_binds=True)
    )


def drop_supplemental_db_objects(engine:Engine):
    engine.execute("drop view if exists daily_scores")
    engine.execute("drop view if exists ride_daylight")
    engine.execute("drop view if exists _build_ride_daylight")
    engine.execute("drop view if exists lbd_athletes")


def create_supplemental_db_objects(engine:Engine):

    # Create VIEWS that may be helpful.

    _v_daily_scores_create = sa.DDL("""
        create view daily_scores as
        select A.team_id, R.athlete_id, sum(R.distance) as distance,
        (sum(R.distance) + IF(sum(R.distance) >= 1.0, 10,0)) as points,
        date(R.start_date) as ride_date
        from rides R
        join athletes A on A.id = R.athlete_id
        group by R.athlete_id, A.team_id, date(R.start_date)
        ;
    """)

    engine.execute(_v_daily_scores_create)

    _v_buid_ride_daylight = sa.DDL("""
        create view _build_ride_daylight as
        select R.id as ride_id, date(R.start_date) as ride_date,
        sec_to_time(R.elapsed_time) as elapsed,
        sec_to_time(R.moving_time) as moving,
        TIME(R.start_date) as start_time,
        TIME(date_add(R.start_date, interval R.elapsed_time second)) as end_time,
        W.sunrise, W.sunset
        from rides R
        join ride_weather W on W.ride_id = R.id
        ;
        """)

    engine.execute(_v_buid_ride_daylight)

    _v_ride_daylight = sa.DDL("""
        create view ride_daylight as
        select ride_id, ride_date, start_time, end_time, sunrise, sunset, moving,
        IF(start_time < sunrise, LEAST(TIMEDIFF(sunrise, start_time), moving), sec_to_time(0)) as before_sunrise,
        IF(end_time > sunset, LEAST(TIMEDIFF(end_time, sunset), moving), sec_to_time(0)) as after_sunset
        from _build_ride_daylight
        ;
        """)

    engine.execute(_v_ride_daylight)

    _v_leaderboard_athletes = sa.DDL("""
        create view lbd_athletes as select a.id, a.name, a.display_name, a.team_id from athletes a
        join teams T on T.id=a.team_id where not T.leaderboard_exclude
        ;
        """)

    engine.execute(_v_leaderboard_athletes)
