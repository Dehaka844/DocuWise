"""add departments and user memberships

Revision ID: 8ac41e2d9f10
Revises: 57cb97ea631b
Create Date: 2026-11-03
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8ac41e2d9f10"
down_revision: Union[str, Sequence[str], None] = "57cb97ea631b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "departments",
        sa.Column("code", sa.String(length=30), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.PrimaryKeyConstraint("code"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "user_departments",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("department_code", sa.String(length=30), nullable=False),
        sa.ForeignKeyConstraint(["department_code"], ["departments.code"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "department_code"),
    )
    op.bulk_insert(
        sa.table(
            "departments",
            sa.column("code", sa.String()),
            sa.column("name", sa.String()),
        ),
        [
            {"code": "rrhh", "name": "Recursos humanos"},
            {"code": "tecnico", "name": "Técnico"},
            {"code": "marketing", "name": "Marketing"},
        ],
    )


def downgrade() -> None:
    op.drop_table("user_departments")
    op.drop_table("departments")
