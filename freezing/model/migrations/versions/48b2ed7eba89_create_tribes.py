import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.mysql import INTEGER

"""create tribes

Revision ID: 48b2ed7eba89
Revises: 21518d40552c
Create Date: 2020-11-19 08:21:36.865982

"""

# revision identifiers, used by Alembic.
revision = "48b2ed7eba89"
down_revision = "21518d40552c"


def upgrade():
    op.create_table(
        "tribes",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        # The ORM definition of athlete_id is BigInteger, to match the ORM
        # definition of athlete.id; however, in the database this column is
        # an INTEGER(11). In order to upgrade an existing database we need
        # to match that type.
        sa.Column(
            "athlete_id",
            INTEGER(11),
            sa.ForeignKey("athletes.id", ondelete="cascade"),
            nullable=False,
            index=True,
        ),
        sa.Column("tribal_group", sa.String(255), nullable=False),
        sa.Column("tribe_name", sa.String(255), nullable=False),
    )
    pass


def downgrade():
    op.drop_table("tribes")
    pass
