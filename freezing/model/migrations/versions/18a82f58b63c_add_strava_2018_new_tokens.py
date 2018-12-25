from alembic import op
import sqlalchemy as sa

"""Add Strava 2018 new tokens

Revision ID: 18a82f58b63c
Revises: c5bfe51cfec3
Create Date: 2018-12-24 14:54:59.725988

"""

# revision identifiers, used by Alembic.
revision = '18a82f58b63c'
down_revision = 'c5bfe51cfec3'


def upgrade():
    op.add_column('athletes', sa.Column(
        'refresh_token', sa.Integer, nullable=True))
    op.add_column('athletes', sa.Column(
        'expires_at', sa.Integer, nullable=False, default=0))


def downgrade():
    op.drop_column('athletes', sa.Column('refresh_token'))
    op.drop_column('athletes', sa.Column('expires_at'))
