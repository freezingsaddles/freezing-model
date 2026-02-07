import sqlalchemy as sa
from alembic import op

"""add wind

Revision ID: 83d3e920ac3d
Revises: 505b1bd433d8
Create Date: 2026-02-07 15:51:23.909769

"""

# revision identifiers, used by Alembic.
revision = "83d3e920ac3d"
down_revision = "505b1bd433d8"


def upgrade():
    op.add_column("ride_weather", sa.Column("wind_speed", sa.Float(), nullable=True))
    op.add_column("ride_weather", sa.Column("wind_gust", sa.Float(), nullable=True))


def downgrade():
    op.drop_column("ride_weather", "wind_speed")
    op.drop_column("ride_weather", "wind_gust")
