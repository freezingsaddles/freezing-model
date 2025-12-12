import sqlalchemy as sa
from alembic import op

"""add ride description

Revision ID: e73674800c6e
Revises: 9ec05cbe5ff5
Create Date: 2025-12-11 17:03:27.241094

"""

# revision identifiers, used by Alembic.
revision = "e73674800c6e"
down_revision = "9ec05cbe5ff5"


def upgrade():
    op.add_column("rides", sa.Column("description", sa.String(1024), nullable=True))
    pass


def downgrade():
    op.drop_column("rides", "description")
    pass
