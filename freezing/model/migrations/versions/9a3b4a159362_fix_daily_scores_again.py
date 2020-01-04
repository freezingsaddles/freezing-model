from alembic import op
from freezing.model.config import config

"""Fix daily scores again

Revision ID: 9a3b4a159362
Revises: f620a24f5f7e
Create Date: 2020-01-04 12:39:50.340608

"""

# revision identifiers, used by Alembic.
revision = '9a3b4a159362'
down_revision = 'f620a24f5f7e'


def upgrade():
    op.execute("""
      create or replace view daily_scores as
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
    """.format(config.TIMEZONE))
    pass


def downgrade():
    op.execute("""
      create or replace view daily_scores as
      select
        A.team_id,
        R.athlete_id,
        sum(R.distance) as distance,
        case
          when sum(R.distance) < 1 then 0
          when sum(R.distance) < 10 then
            10 + 0.5 * (21 * sum(R.distance) -
            (sum(R.distance) * sum(R.distance)))
          else 65 + sum(R.distance)
        end as points,
        date(CONVERT_TZ(R.start_date, R.timezone,'{0}')) as ride_date
           from
        rides R join athletes A on A.id = R.athlete_id
      group by
        A.id,
        A.team_id,
        ride_date
      ;
    """.format(config.TIMEZONE))
    pass
