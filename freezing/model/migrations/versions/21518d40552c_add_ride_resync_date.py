from alembic import op
import sqlalchemy as sa

"""add ride resync date

Revision ID: 21518d40552c
Revises: d4be89cbab08
Create Date: 2020-02-01 08:53:33.632416

"""

# revision identifiers, used by Alembic.
revision = '21518d40552c'
down_revision = 'd4be89cbab08'


def upgrade():
    op.add_column('rides', sa.Column('resync_date', sa.DateTime, nullable=True))
    # we do not know which rides have partial efforts fetched so schedule them all for resync over the next few days
    op.execute('update rides set efforts_fetched = false, resync_count = 1, resync_date = now() + interval floor(rand() * 72) hour')
    pass


def downgrade():
    op.drop_column('rides', 'resync_date')
    pass
