import sqlalchemy as sa
from alembic import op

"""least-variance

Revision ID: f620a24f5f7e
Revises: b4d003c71167
Create Date: 2020-01-03 23:06:50.491509

"""

# revision identifiers, used by Alembic.
revision = "f620a24f5f7e"
down_revision = "b4d003c71167"


def upgrade():
    op.execute(
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


def downgrade():
    op.execute(
        """
               drop view variance_by_day
               ;
               """
    )
