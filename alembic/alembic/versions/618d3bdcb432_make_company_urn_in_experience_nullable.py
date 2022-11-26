"""Make company_urn in experience nullable

Revision ID: 618d3bdcb432
Revises: 3b22680d8fa7
Create Date: 2022-11-18 20:03:54.909426

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = "618d3bdcb432"
down_revision = "3b22680d8fa7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "experience",
        "company_urn",
        existing_type=sa.VARCHAR(),
        nullable=True,
    )


def downgrade() -> None:
    table_name = sa.sql.table("experience", sa.Column("company_urn", sa.VARCHAR()))
    op.execute(
        table_name.update()
        .where(table_name.c.company_urn is None)
        .values(company_urn="")
    )
    op.alter_column(
        "experience",
        "company_urn",
        existing_type=sa.VARCHAR(),
        nullable=False,
    )
