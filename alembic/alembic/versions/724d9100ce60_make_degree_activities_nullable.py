"""Make degree & activities nullable

Revision ID: 724d9100ce60
Revises: afdb9eb69331
Create Date: 2022-11-18 18:55:36.852764

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "724d9100ce60"
down_revision = "afdb9eb69331"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "education",
        "degree",
        existing_type=sa.VARCHAR(),
        nullable=True,
    )
    op.alter_column(
        "education",
        "activities",
        existing_type=sa.VARCHAR(),
        nullable=True,
    )


def downgrade() -> None:
    table_name = sa.sql.table("education", sa.Column("degree", sa.VARCHAR()))
    op.execute(table_name.update().where(table_name.c.degree is None).values(degree=""))
    op.alter_column(
        "education",
        "degree",
        existing_type=sa.VARCHAR(),
        nullable=False,
        schema="schema_name",
    )

    table_name = sa.sql.table("education", sa.Column("activities", sa.VARCHAR()))
    op.execute(
        table_name.update().where(table_name.c.activities is None).values(activities="")
    )
    op.alter_column(
        "education",
        "activities",
        existing_type=sa.VARCHAR(),
        nullable=False,
        schema="schema_name",
    )
