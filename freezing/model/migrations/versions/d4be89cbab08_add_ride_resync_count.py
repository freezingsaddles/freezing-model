from alembic import op
import sqlalchemy as sa

"""add ride resync count

Revision ID: d4be89cbab08
Revises: 9a3b4a159362
Create Date: 2020-01-16 23:03:57.392052

"""

# revision identifiers, used by Alembic.
revision = "d4be89cbab08"
down_revision = "9a3b4a159362"


def upgrade():
    op.add_column(
        "rides", sa.Column("resync_count", sa.Integer, nullable=False, default=0)
    )
    op.execute(
        "update rides set efforts_fetched = false where id not in (select ride_id from ride_efforts)"
    )
    pass


def downgrade():
    op.drop_column("rides", "resync_count")
    pass
