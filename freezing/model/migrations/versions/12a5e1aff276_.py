from alembic import op
import sqlalchemy as sa
from freezing.model.config import config

"""Make daily_scores pay attention to timezones

Revision ID: 12a5e1aff276
Revises: dd2e35777af9
Create Date: 2019-01-13 23:14:55.897733

"""

# revision identifiers, used by Alembic.
revision = "12a5e1aff276"
down_revision = "dd2e35777af9"


def upgrade():
    op.execute(
        """
        CREATE OR REPLACE VIEW daily_scores AS
        select
            A.team_id,
            R.athlete_id,
            sum(R.distance) as distance,
            (sum(R.distance) + IF(sum(R.distance) >= 1.0, 10,0)) as points,
            date(CONVERT_TZ(R.start_date, R.timezone,'{0}')) as ride_date
        from
            rides R join athletes A on A.id = R.athlete_id
        group by
          R.athlete_id,
          A.team_id,
          date(CONVERT_TZ(R.start_date, R.timezone,'{0}'))
        ;
    """.format(
            config.TIMEZONE
        )
    )


def downgrade():
    op.execute(
        """
        CREATE OR REPLACE VIEW `daily_scores` AS
        select
            `A`.`team_id` AS `team_id`,
            `R`.`athlete_id` AS `athlete_id`,
            sum(`R`.`distance`) AS `distance`,
            (sum(`R`.`distance`) + if((sum(`R`.`distance`) >= 1.0),10,0)) AS `points`,
            cast(`R`.`start_date` as date) AS `ride_date`
        from
        (
            `rides` `R` join `athletes` `A` on((`A`.`id` = `R`.`athlete_id`))
        )
        group by
            `R`.`athlete_id`,
            `A`.`team_id`,
            cast(`R`.`start_date` as date)
       ;
    """
    )
