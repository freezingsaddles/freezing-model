import sqlalchemy as sa
from alembic import op

"""add pr/local legend to ride efforts

Revision ID: fb2de6b9caf1
Revises: 48b2ed7eba89
Create Date: 2025-11-24 14:32:29.625338

"""

# revision identifiers, used by Alembic.
revision = "fb2de6b9caf1"
down_revision = "48b2ed7eba89"


def upgrade():
    op.add_column(
        "ride_efforts", sa.Column("personal_record", sa.Integer, nullable=True)
    )
    op.add_column("ride_efforts", sa.Column("local_legend", sa.Boolean, nullable=True))
    pass


def downgrade():
    op.drop_column("ride_efforts", "personal_record")
    op.drop_column("ride_efforts", "local_legend")
    pass
