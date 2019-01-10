from alembic import op

"""Fix week definition to be ISO 8601 compliant

Fixes https://github.com/freezingsaddles/freezing-model/issues/13

week(some_date,3) is the same as weekofyear(date) and should conform
to ISO 8601.

Revision ID: dd2e35777af9
Revises: 23c3b1c5ffb0
Create Date: 2019-01-10 16:39:55.065136

"""

# revision identifiers, used by Alembic.
revision = 'dd2e35777af9'
down_revision = '23c3b1c5ffb0'


def upgrade():
    op.execute("""
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
                week(`daily_scores`.`ride_date`,3);
    """)


def downgrade():
    op.execute("""
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
       drop view if exists weekly_stats;
    """)
