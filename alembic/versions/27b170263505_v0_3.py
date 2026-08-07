"""v0_3

Revision ID: 27b170263505
Revises: 3c27d5cf79f9
Create Date: 2026-07-12 17:38:53.311616

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "27b170263505"
down_revision: Union[str, Sequence[str], None] = "3c27d5cf79f9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    gender_enum = postgresql.ENUM(
        "male", "female", name="genderenum", create_type=False
    )
    gender_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "profiles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=50), nullable=True),
        sa.Column("surname", sa.String(length=50), nullable=True),
        sa.Column("gender", gender_enum, nullable=False),
        sa.Column("picture", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("phone"),
        sa.UniqueConstraint("user_id"),
    )
    op.add_column(
        "users",
        sa.Column(
            "is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "is_admin", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "is_superuser",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
    )
    op.alter_column(
        "users",
        "created_at",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=False,
        existing_server_default=sa.text("now()"),
    )
    op.alter_column(
        "users",
        "updated_at",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=False,
        existing_server_default=sa.text("now()"),
    )
    op.drop_constraint(op.f("users_phone_key"), "users", type_="unique")
    op.drop_constraint(op.f("users_username_key"), "users", type_="unique")
    op.drop_column("users", "surname")
    op.drop_column("users", "username")
    op.drop_column("users", "phone")
    op.drop_column("users", "name")


def downgrade() -> None:
    op.add_column(
        "users",
        sa.Column("name", sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    )
    op.add_column(
        "users",
        sa.Column("phone", sa.VARCHAR(length=20), autoincrement=False, nullable=True),
    )
    op.add_column(
        "users",
        sa.Column(
            "username", sa.VARCHAR(length=50), autoincrement=False, nullable=False
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "surname", sa.VARCHAR(length=50), autoincrement=False, nullable=False
        ),
    )
    op.create_unique_constraint(
        op.f("users_username_key"),
        "users",
        ["username"],
        postgresql_nulls_not_distinct=False,
    )
    op.create_unique_constraint(
        op.f("users_phone_key"), "users", ["phone"], postgresql_nulls_not_distinct=False
    )
    op.alter_column(
        "users",
        "updated_at",
        existing_type=sa.DateTime(),
        type_=postgresql.TIMESTAMP(timezone=True),
        existing_nullable=False,
        existing_server_default=sa.text("now()"),
    )
    op.alter_column(
        "users",
        "created_at",
        existing_type=sa.DateTime(),
        type_=postgresql.TIMESTAMP(timezone=True),
        existing_nullable=False,
        existing_server_default=sa.text("now()"),
    )
    op.drop_column("users", "is_superuser")
    op.drop_column("users", "is_admin")
    op.drop_column("users", "is_active")
    op.drop_table("profiles")
