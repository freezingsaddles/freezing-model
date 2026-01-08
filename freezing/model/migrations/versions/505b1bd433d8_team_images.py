import sqlalchemy as sa
from alembic import op

"""team images

Revision ID: 505b1bd433d8
Revises: e73674800c6e
Create Date: 2026-01-08 17:00:18.303585

"""

# revision identifiers, used by Alembic.
revision = "505b1bd433d8"
down_revision = "e73674800c6e"


def upgrade():
    op.add_column("teams", sa.Column("cover_photo", sa.String(255), nullable=True))
    op.add_column("teams", sa.Column("profile_photo", sa.String(255), nullable=True))


def downgrade():
    op.drop_column("teams", "profile_photo")
    op.drop_column("teams", "cover_photo")
