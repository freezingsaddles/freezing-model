import sqlalchemy as sa
from alembic import op

"""Create weekly_stats view

This is needed for the 100-point-per-week mileage score cap
See: https://github.com/freezingsaddles/freezing-web/issues/65

Revision ID: 23c3b1c5ffb0
Revises: b4b227f95848
Create Date: 2019-01-09 21:26:35.969334

"""

# revision identifiers, used by Alembic.
revision = "23c3b1c5ffb0"
down_revision = "b4b227f95848"


def upgrade():
    op.execute(
        """
        create or replace VIEW `weekly_stats` AS
            select
                `daily_scores`.`athlete_id` AS `athlete_id`,
                `teams`.`id` as `team_id`,
                `teams`.`name` as `team_name`,
                week(`daily_scores`.`ride_date`,0) AS `week_num`,
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
                week(`daily_scores`.`ride_date`,0);
    """
    )


def downgrade():
    op.execute(
        """
       drop view if exists weekly_stats;
    """
    )
