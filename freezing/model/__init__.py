import re
import warnings
import json
from typing import Dict, Any

from alembic import command

import sqlalchemy as sa
from freezing.model.exc import DatabaseVersionError
from sqlalchemy import orm, inspect, create_engine

from sqlalchemy.engine import Engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import Pool
from sqlalchemy.sql.expression import Executable, ClauseElement
from sqlalchemy.types import TypeDecorator, TEXT

from . import meta, migrationsutil
from .autolog import log

Base = declarative_base(metadata=meta.metadata)

class _SqlView:
    """ Empty class used to indicate that this is a SQL View and not to be created. """
    pass


def init_model(*, sqlalchemy_url:str, alembic_repository:str, drop:bool=False, check_version:bool=True):
    """
    Initializes the tables and classes of the model using configured engine.

    :param sqlalchemy_url: The database URI.
    :param alembic_repository: The path to the alembic repository (migrations).
    :param drop: Whether to drop the tables first.
    :param check_version: Whether to ensure that the database version is up-to-date.
    """
    engine = create_engine(sqlalchemy_url)

    sm = orm.sessionmaker(autoflush=True, autocommit=False, bind=engine)
    meta.engine = engine
    meta.Session = orm.scoped_session(sm)

    alembic_cfg = migrationsutil.create_config(sqlalchemy_url=None)

    # Check to see whether the database has already been created or not.
    # Based on this, we know whether we need to upgrade the database or mark the database
    # as the latest version.

    inspector = inspect(engine)

    db_objects_created = len(inspector.get_table_names()) > 1

    fresh_db = False

    if not db_objects_created:
        log.info("Database apears uninitialized, creating database tables")
        meta.metadata.create_all(engine, checkfirst=True)
        fresh_db = True
    elif drop:
        log.info("Dropping database tables and re-creating.")
        meta.metadata.drop_all(engine, checkfirst=True)
        meta.metadata.create_all(engine)
        fresh_db = True

    if fresh_db:
        command.stamp(alembic_cfg, "head")
    else:
        # If existing is *newer* than installed, then attempt to upgrade.
        # We could walk the revisions to determine this ... or just attempt an upgrade and catch an "unknown"
        # error.
        #
        # (Walking revisions)
        # for sc in script.walk_revisions(
        #       base=base or "base",
        #        head=head or "heads"):
        #    config.print_stdout(
        #        sc.cmd_format(
        #            verbose=verbose, include_branches=True,
        #            include_doc=True, include_parents=True))

        if check_version:
            latest = migrationsutil.get_head_version()
            installed = migrationsutil.get_database_version()
            if latest != installed:
                warnings.warn("Installed database ({0}) does not match latest available ({1}). (ignoring for now)".format(installed, latest), UserWarning)
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
