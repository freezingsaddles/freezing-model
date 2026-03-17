import sqlalchemy as sa
from alembic import op

"""add ride type

Revision ID: d1119fc76e42
Revises: 83d3e920ac3d
Create Date: 2026-03-17 18:52:15.915428

"""

# revision identifiers, used by Alembic.
revision = "d1119fc76e42"
down_revision = "83d3e920ac3d"


def upgrade():
    op.add_column("rides", sa.Column("ride_type", sa.String(255), nullable=True))
    op.drop_column("rides", "trainer")


def downgrade():
    op.drop_column("rides", "ride_type")
    op.add_column("rides", sa.Column("trainer", sa.Boolean(), nullable=True))
