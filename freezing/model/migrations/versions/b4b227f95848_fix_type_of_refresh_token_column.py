from alembic import op
import sqlalchemy as sa

"""Fix type of refresh_token column

Revision ID: b4b227f95848
Revises: 18a82f58b63c
Create Date: 2018-12-27 17:35:07.036017

"""

# revision identifiers, used by Alembic.
revision = "b4b227f95848"
down_revision = "18a82f58b63c"


def upgrade():
    op.drop_column("athletes", "refresh_token")
    op.add_column("athletes", sa.Column("refresh_token", sa.String(255), nullable=True))


def downgrade():
    op.drop_column("athletes", "refresh_token")
    op.add_column("athletes", sa.Column("refresh_token", sa.Integer, nullable=True))
