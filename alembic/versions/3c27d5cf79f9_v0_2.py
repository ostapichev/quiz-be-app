"""v0.2

Revision ID: 3c27d5cf79f9
Revises: 3827c994d641
Create Date: 2026-03-15 12:12:46.221858

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "3c27d5cf79f9"
down_revision: Union[str, Sequence[str], None] = "3827c994d641"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users", sa.Column("hashed_password", sa.String(length=255), nullable=True)
    )
    op.alter_column(
        "users",
        "name",
        existing_type=sa.VARCHAR(length=20),
        type_=sa.String(length=50),
        existing_nullable=False,
    )
    op.alter_column(
        "users",
        "surname",
        existing_type=sa.VARCHAR(length=30),
        type_=sa.String(length=50),
        existing_nullable=False,
    )
    op.alter_column(
        "users",
        "username",
        existing_type=sa.VARCHAR(length=30),
        type_=sa.String(length=50),
        existing_nullable=False,
    )
    op.alter_column(
        "users",
        "email",
        existing_type=sa.VARCHAR(length=30),
        type_=sa.String(length=255),
        existing_nullable=False,
    )
    op.alter_column(
        "users",
        "phone",
        existing_type=sa.VARCHAR(length=12),
        type_=sa.String(length=20),
        nullable=True,
    )
    op.drop_column("users", "password")


def downgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "password", sa.VARCHAR(length=255), autoincrement=False, nullable=True
        ),
    )
    op.alter_column(
        "users",
        "phone",
        existing_type=sa.String(length=20),
        type_=sa.VARCHAR(length=12),
        nullable=False,
    )
    op.alter_column(
        "users",
        "email",
        existing_type=sa.String(length=255),
        type_=sa.VARCHAR(length=30),
        existing_nullable=False,
    )
    op.alter_column(
        "users",
        "username",
        existing_type=sa.String(length=50),
        type_=sa.VARCHAR(length=30),
        existing_nullable=False,
    )
    op.alter_column(
        "users",
        "surname",
        existing_type=sa.String(length=50),
        type_=sa.VARCHAR(length=30),
        existing_nullable=False,
    )
    op.alter_column(
        "users",
        "name",
        existing_type=sa.String(length=50),
        type_=sa.VARCHAR(length=20),
        existing_nullable=False,
    )
    op.drop_column("users", "hashed_password")
