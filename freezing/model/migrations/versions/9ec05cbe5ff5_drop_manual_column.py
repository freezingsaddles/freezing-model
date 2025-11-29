import sqlalchemy as sa
from alembic import op

"""drop manual column

Revision ID: 9ec05cbe5ff5
Revises: 3e51578560f0
Create Date: 2025-11-29 16:07:15.651307

"""

# revision identifiers, used by Alembic.
revision = "9ec05cbe5ff5"
down_revision = "3e51578560f0"


def upgrade():
    op.drop_column("rides", "manual")
    pass


def downgrade():
    op.add_column(
        "rides",
        sa.Column("manual", sa.Boolean, nullable=True),
    )
    pass
