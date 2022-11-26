"""Init models

Revision ID: afdb9eb69331
Revises:
Create Date: 2022-11-18 18:30:47.667284

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "afdb9eb69331"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "company",
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, onupdate=sa.func.now()),
        sa.Column("urn_id", sa.Integer, primary_key=True, nullable=False),
        sa.Column("url", sa.VARCHAR(), nullable=False),
        sa.Column("staff_count", sa.Integer, nullable=False),
        sa.Column("specialities", sa.ARRAY(sa.VARCHAR()), nullable=False),
        sa.Column("name", sa.VARCHAR(), nullable=False),
        sa.Column("symbol", sa.VARCHAR(), nullable=False),
    )
    op.create_table(
        "people",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement="auto"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, onupdate=sa.func.now()),
        sa.Column("industry_name", sa.VARCHAR(), nullable=False),
        sa.Column("first_name", sa.VARCHAR(), nullable=False),
        sa.Column("last_name", sa.VARCHAR(), nullable=False),
        sa.Column("student", sa.Boolean(), nullable=False),
        sa.Column("country", sa.VARCHAR(), nullable=False),
        sa.Column("city", sa.VARCHAR(), nullable=False),
    )
    op.create_table(
        "education",
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, onupdate=sa.func.now()),
        sa.Column("id", sa.Integer, primary_key=True, autoincrement="auto"),
        sa.Column("degree", sa.VARCHAR(), nullable=False),
        sa.Column("activities", sa.VARCHAR(), nullable=False),
        sa.Column("name", sa.VARCHAR(), nullable=False),
        sa.Column("field", sa.VARCHAR(), nullable=False),
        sa.Column("start", sa.DateTime, nullable=False),
        sa.Column("end", sa.DateTime, nullable=True),
    )
    op.create_table(
        "experience",
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, onupdate=sa.func.now()),
        sa.Column("id", sa.Integer, primary_key=True, autoincrement="auto"),
        sa.Column("location", sa.VARCHAR(), nullable=False),
        sa.Column("company_name", sa.VARCHAR(), nullable=False),
        sa.Column("company_urn", sa.VARCHAR(), nullable=False),
        sa.Column("title", sa.VARCHAR(), nullable=False),
        sa.Column("start", sa.DateTime, nullable=False),
        sa.Column("end", sa.DateTime, nullable=True),
    )
    op.create_table(
        "locations",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement="auto"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, onupdate=sa.func.now()),
        sa.Column(
            "company_urn_id",
            sa.Integer,
            sa.ForeignKey("company.urn_id"),
            nullable=False,
        ),
        sa.Column("country", sa.VARCHAR(), nullable=False),
        sa.Column("geographic_area", sa.VARCHAR(), nullable=False),
        sa.Column("city", sa.VARCHAR(), nullable=False),
        sa.Column("postal_code", sa.VARCHAR(), nullable=False),
        sa.Column("line", sa.VARCHAR(), nullable=False),
        sa.Column("headquarter", sa.Boolean(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("company")
    op.drop_table("people")
    op.drop_table("education")
    op.drop_table("experience")
    op.drop_table("locations")
