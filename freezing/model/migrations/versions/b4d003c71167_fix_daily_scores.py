from alembic import op
from freezing.model.config import config

"""Fix daily scores

Revision ID: b4d003c71167
Revises: 9b7cf7603b70
Create Date: 2020-01-01 18:34:17.817054

"""

# revision identifiers, used by Alembic.
revision = "b4d003c71167"
down_revision = "9b7cf7603b70"


def upgrade():
    op.execute(
        """
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
    """.format(
            config.TIMEZONE
        )
    )
    pass


def downgrade():
    op.execute(
        """
        create or replace VIEW `daily_scores` as
        select A.team_id, R.athlete_id, sum(R.distance) as distance,
        case
            when distance < 0 then 0
            when distance < 10 then 10 + 0.5 *
                (21 * distance - (distance * distance))
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
    """.format(
            config.TIMEZONE
        )
    )
    pass
