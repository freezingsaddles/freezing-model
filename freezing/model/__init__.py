import warnings

import sqlalchemy as sa
from alembic import command
from alembic.script import ScriptDirectory
from alembic.util import CommandError
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql.expression import ClauseElement, Executable

from freezing.model import meta, migrationsutil
from freezing.model.autolog import log
from freezing.model.config import config
from freezing.model.monkeypatch import collections
from freezing.model.orm import (
    Athlete,
    Ride,
    RideEffort,
    RideError,
    RideGeo,
    RidePhoto,
    RideTrack,
    RideWeather,
    Team,
    Tribe,
)

# Make the list of managed tables explicit here.
# These tables will be automatically created by sqlalchemy in init_model
# if they do not exist *and* the database appears to be empty.
MANAGED_TABLES = [
    Team.__table__,
    Athlete.__table__,
    RideError.__table__,
    Ride.__table__,
    RideGeo.__table__,
    RideTrack.__table__,
    RideEffort.__table__,
    RidePhoto.__table__,
    RideWeather.__table__,
    Tribe.__table__,
]


def init_db():
    init_model(config.SQLALCHEMY_URL)


def init_model(sqlalchemy_url: str, drop: bool = False, check_version: bool = True):
    """
    Initializes the tables and classes of the model using configured engine.

    :param sqlalchemy_url: The database URI.
    :param drop: Whether to drop the tables first.
    :param check_version: Whether to ensure that the database version is up-to-date.
    """
    # Monkeypatch Collections to get old alembic version to work
    collections()
    engine = create_engine(
        sqlalchemy_url, pool_recycle=3600
    )  # pool_recycle is for mysql

    sm = sessionmaker(autoflush=True, autocommit=False, bind=engine)
    meta.engine = engine
    meta.scoped_session = scoped_session(sm)

    alembic_cfg = migrationsutil.create_config(sqlalchemy_url=sqlalchemy_url)

    alembic_script = ScriptDirectory.from_config(alembic_cfg)

    # Check to see whether the database has already been created or not.
    # Based on this, we know whether we need to upgrade the database or
    # mark the database as the latest version.

    inspector = Inspector.from_engine(engine)

    db_objects_created = len(inspector.get_table_names()) > 1

    fresh_db = False

    if not db_objects_created:
        log.info("Database appears uninitialized, creating database tables")
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
                warnings.warn(
                    "Unknown db revision {} installed, ignoring db upgrade.".format(
                        installed
                    )
                )
            else:
                if latest != installed:
                    log.info(
                        "Installed database ({0}) does not match latest available ({1}). (UPGRADING)".format(
                            installed, latest
                        ),
                        UserWarning,
                    )
                    command.upgrade(alembic_cfg, "head")
        else:
            log.info("Skipping database upgrade.")


class CreateView(Executable, ClauseElement):
    def __init__(self, name, select):
        self.name = name
        self.select = select


@compiles(CreateView, "mysql")
def visit_create_view(element, compiler, **kw):
    return "CREATE VIEW IF NOT EXISTS %s AS %s" % (
        element.name,
        compiler.process(element.select, literal_binds=True),
    )


def drop_supplemental_db_objects(engine: Engine):
    engine.execute("drop view if exists daily_scores")
    engine.execute("drop view if exists ride_daylight")
    engine.execute("drop view if exists _build_ride_daylight")
    engine.execute("drop view if exists lbd_athletes")


def create_supplemental_db_objects(engine: Engine):
    # Create VIEWS that may be helpful.

    _v_daily_scores_create = sa.DDL(
        """
        create view daily_scores as
        select
          A.team_id,
          R.athlete_id,
          sum(R.distance) as distance,
          case
            when sum(R.distance) < 1 then 0
            when sum(R.distance) < 10 then
              10 + 0.5 * (21 * sum(R.distance) -
              (sum(R.distance) * sum(R.distance)))
            else 65 + sum(R.distance) - 10
          end as points,
          date(CONVERT_TZ(R.start_date, R.timezone,'{0}')) as ride_date
        from
          rides R join athletes A on A.id = R.athlete_id
        group by
          A.id,
          A.team_id,
          ride_date
        ;
    """.format(
            config.TIMEZONE
        )
    )

    engine.execute(_v_daily_scores_create)

    _v_buid_ride_daylight = sa.DDL(
        """
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
        """
    )

    engine.execute(_v_buid_ride_daylight)

    _v_ride_daylight = sa.DDL(
        """
        create view ride_daylight as
        select ride_id, ride_date, start_time, end_time, sunrise, sunset, moving,
        IF(start_time < sunrise, LEAST(TIMEDIFF(sunrise, start_time), moving), sec_to_time(0)) as before_sunrise,
        IF(end_time > sunset, LEAST(TIMEDIFF(end_time, sunset), moving), sec_to_time(0)) as after_sunset
        from _build_ride_daylight
        ;
        """
    )

    engine.execute(_v_ride_daylight)

    _v_leaderboard_athletes = sa.DDL(
        """
       create view lbd_athletes as select a.id, a.name, a.display_name, a.team_id from athletes a
        join teams T on T.id=a.team_id where not T.leaderboard_exclude
        ;
        """
    )

    engine.execute(_v_leaderboard_athletes)

    _v_100_mile_team_score = sa.DDL(
        """
        create or replace VIEW `weekly_stats` AS
            select
                `daily_scores`.`athlete_id` AS `athlete_id`,
                `teams`.`id` as `team_id`,
                `teams`.`name` as `team_name`,
                week(`daily_scores`.`ride_date`,3) AS `week_num`,
                (
                    select sum(
                        case
                            when `daily_scores`.`distance` >= 1
                            then 1
                            else 0
                        end
                    )
                ) as `days`,
                sum(`daily_scores`.`distance`) AS `distance`,
                sum(`daily_scores`.`points`) AS `points`,
                (select case
                    when sum(`daily_scores`.`distance`) < 100
                    then sum(`daily_scores`.`distance`)
                    else (100)
                    end
                ) as team_distance
            from
                `daily_scores` join `teams`
                    on `teams`.`id` = `daily_scores`.`team_id`
            where not `teams`.`leaderboard_exclude`
            group by
                `daily_scores`.`team_id`,
                `daily_scores`.`athlete_id`,
                week(`daily_scores`.`ride_date`,3)
        ;
        """
    )

    engine.execute(_v_100_mile_team_score)

    _v_daily_variance = sa.DDL(
        """
             create or replace view variance_by_day as
                select
                  ds.athlete_id,
                  sum(case when ds.distance >= 1 then 1 else 0 end) ride_days,
                  sum(distance) total_miles,
                  var_pop(case when dayofweek(ds.ride_date)=1
                               then ds.distance end) sun_var_pop,
                  var_pop(case when dayofweek(ds.ride_date)=2
                               then ds.distance end) mon_var_pop,
                  var_pop(case when dayofweek(ds.ride_date)=3
                               then ds.distance end) tue_var_pop,
                  var_pop(case when dayofweek(ds.ride_date)=4
                               then ds.distance end) wed_var_pop,
                  var_pop(case when dayofweek(ds.ride_date)=5
                               then ds.distance end) thu_var_pop,
                  var_pop(case when dayofweek(ds.ride_date)=6
                               then ds.distance end) fri_var_pop,
                  var_pop(case when dayofweek(ds.ride_date)=7
                               then ds.distance end) sat_var_pop
                from
                  daily_scores ds
                group by ds.athlete_id;
            """
    )

    engine.execute(_v_daily_variance)
