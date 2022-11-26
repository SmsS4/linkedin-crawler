"""Change datetimes to Integer(year)

Revision ID: 99ae21a13877
Revises: 724d9100ce60
Create Date: 2022-11-18 19:04:54.384319

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "99ae21a13877"
down_revision = "724d9100ce60"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("education", "start")
    op.drop_column("education", "end")
    op.drop_column("experience", "start")
    op.drop_column("experience", "end")
    op.add_column("education", sa.Column("start", sa.Integer(), nullable=True))
    op.add_column("education", sa.Column("end", sa.Integer(), nullable=True))
    op.add_column("experience", sa.Column("start", sa.Integer(), nullable=True))
    op.add_column("experience", sa.Column("end", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("education", "start")
    op.drop_column("education", "end")
    op.drop_column("experience", "start")
    op.drop_column("experience", "end")
    op.add_column("education", sa.Column("start", sa.DateTime, nullable=True))
    op.add_column("education", sa.Column("end", sa.DateTime, nullable=True))
    op.add_column("experience", sa.Column("start", sa.DateTime, nullable=True))
    op.add_column("experience", sa.Column("end", sa.DateTime, nullable=True))
