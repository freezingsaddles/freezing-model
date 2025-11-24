"""photos_fetched null

Revision ID: 54627e8199c9
Revises: 1259f25794b5
Create Date: 2016-01-28 21:11:56.199158

"""

# revision identifiers, used by Alembic.
revision = "54627e8199c9"
down_revision = "1259f25794b5"

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.alter_column(
        "rides",
        "photos_fetched",
        nullable=True,
        server_default=None,
        existing_type=sa.Boolean,
    )


def downgrade():
    op.alter_column(
        "rides",
        "photos_fetched",
        nullable=False,
        server_default=False,
        existing_type=sa.Boolean,
    )
