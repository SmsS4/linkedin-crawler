"""Make some cols nullable

Revision ID: 8696e1942b9a
Revises: 618d3bdcb432
Create Date: 2022-11-18 20:40:16.579126

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = "8696e1942b9a"
down_revision = "618d3bdcb432"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "experience",
        "start",
        existing_type=sa.Integer(),
        nullable=True,
    )
    op.alter_column(
        "education",
        "start",
        existing_type=sa.Integer(),
        nullable=True,
    )
    op.alter_column(
        "education",
        "field",
        existing_type=sa.VARCHAR(),
        nullable=True,
    )
    op.alter_column(
        "people",
        "city",
        existing_type=sa.VARCHAR(),
        nullable=True,
    )


def downgrade() -> None:
    raise Exception("no downgrade for you =(")
