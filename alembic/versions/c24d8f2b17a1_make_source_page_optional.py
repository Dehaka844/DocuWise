"""make source page optional for non-PDF documents

Revision ID: c24d8f2b17a1
Revises: 8ac41e2d9f10
Create Date: 2026-11-04
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c24d8f2b17a1"
down_revision: Union[str, Sequence[str], None] = "8ac41e2d9f10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "message_sources",
        "page_number",
        existing_type=sa.Integer(),
        nullable=True,
    )
    op.execute(
        """
        UPDATE message_sources
        SET page_number = NULL
        WHERE LOWER(filename) NOT LIKE '%.pdf'
        """
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE message_sources
        SET page_number = 1
        WHERE page_number IS NULL
        """
    )
    op.alter_column(
        "message_sources",
        "page_number",
        existing_type=sa.Integer(),
        nullable=False,
    )
