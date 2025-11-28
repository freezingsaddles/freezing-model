import sqlalchemy as sa
from alembic import op

"""add ride temp

Revision ID: 3e51578560f0
Revises: 07849cbfaed7
Create Date: 2025-11-28 13:17:08.078865

"""

# revision identifiers, used by Alembic.
revision = "3e51578560f0"
down_revision = "07849cbfaed7"


def upgrade():
    op.add_column("rides", sa.Column("average_temp", sa.Integer, nullable=True))
    pass


def downgrade():
    op.drop_column("rides", "average_temp")
    pass
