"""
Add access token to athletes table.

Revision ID: 3361172cfdc9
Revises: None
Create Date: 2013-12-07 20:39:16.552480

"""

# revision identifiers, used by Alembic.
revision = "3361172cfdc9"
down_revision = None

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.add_column("athletes", sa.Column("access_token", sa.String(255)))


def downgrade():
    op.drop_column("athletes", "access_token")
