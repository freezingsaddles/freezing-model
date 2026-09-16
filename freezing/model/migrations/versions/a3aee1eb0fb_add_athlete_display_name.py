"""add athlete display name

Revision ID: a3aee1eb0fb
Revises: 3361172cfdc9
Create Date: 2013-12-13 21:07:17.918398

"""

# revision identifiers, used by Alembic.
revision = "a3aee1eb0fb"
down_revision = "3361172cfdc9"

import sqlalchemy as sa
from alembic import op


def upgrade():
    conn = op.get_bind()
    result = conn.execute(
        sa.text(
            "SELECT COUNT(*) FROM information_schema.columns "
            "WHERE table_schema = DATABASE() "
            "AND table_name = 'athletes' "
            "AND column_name = 'display_name'"
        )
    )
    if result.scalar() == 0:
        op.add_column("athletes", sa.Column("display_name", sa.String(255)))


def downgrade():
    op.drop_column("athletes", "display_name")
