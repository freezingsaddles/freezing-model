from alembic import op
import sqlalchemy as sa
from freezing.model.config import config as model_config

"""Update daily_scores view to refelect declining points for first 10 miles

Revision ID: 9b7cf7603b70
Revises: c8add074d30f
Create Date: 2019-12-14 11:38:19.648650

"""

# revision identifiers, used by Alembic.
revision = '9b7cf7603b70'
down_revision = 'c8add074d30f'

def upgrade():
    op.execute("""
        create or replace VIEW `daily_scores` as
        select A.team_id, R.athlete_id, sum(R.distance) as distance,
        case
            when distance < 0 then 0
            when distance < 10 then 10 + 0.5 * (21 * distance - (distance * distance))
            else 65 + distance
        end as points,
        date(CONVERT_TZ(R.start_date, R.timezone,'{0}')) as ride_date
        from rides R
        join athletes A on A.id = R.athlete_id
        group by
          R.athlete_id,
          A.team_id,
          date(CONVERT_TZ(R.start_date, R.timezone,'{0}'))
        ;
        """).format(model_config.TIMEZONE))


def downgrade():
    op.execute("""
        create or replace view daily_scores as
        select A.team_id, R.athlete_id, sum(R.distance) as distance,
        (sum(R.distance) + IF(sum(R.distance) >= 1.0, 10,0)) as points,
        date(CONVERT_TZ(R.start_date, R.timezone,'{0}')) as ride_date
        from rides R
        join athletes A on A.id = R.athlete_id
        group by
          R.athlete_id,
          A.team_id,
          date(CONVERT_TZ(R.start_date, R.timezone,'{0}'))
        ;
    """.format(model_config.TIMEZONE))
