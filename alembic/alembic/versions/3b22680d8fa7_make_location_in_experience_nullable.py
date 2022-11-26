"""Make location in experience nullable

Revision ID: 3b22680d8fa7
Revises: 99ae21a13877
Create Date: 2022-11-18 19:56:49.269228

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = "3b22680d8fa7"
down_revision = "99ae21a13877"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "experience",
        "location",
        existing_type=sa.VARCHAR(),
        nullable=True,
    )


def downgrade() -> None:
    table_name = sa.sql.table("experience", sa.Column("location", sa.VARCHAR()))
    op.execute(
        table_name.update().where(table_name.c.location is None).values(location="")
    )
    op.alter_column(
        "experience",
        "location",
        existing_type=sa.VARCHAR(),
        nullable=False,
    )
