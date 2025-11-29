import sqlalchemy as sa
from alembic import op

"""add activity visibility

Revision ID: 07849cbfaed7
Revises: fb2de6b9caf1
Create Date: 2025-11-27 09:13:16.402120

"""

# revision identifiers, used by Alembic.
revision = "07849cbfaed7"
down_revision = "fb2de6b9caf1"


def upgrade():
    op.add_column("rides", sa.Column("visibility", sa.String(255), nullable=True))
    pass


def downgrade():
    op.drop_column("rides", "visibility")
    pass
