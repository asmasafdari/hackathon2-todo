"""Add hashed_password to users table for Clerk auth

Revision ID: 002_add_hashed_password
Revises: 001_initial
Create Date: 2026-02-15

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "002_add_hashed_password"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("hashed_password", sa.String(), nullable=False, server_default="clerk-managed"),
    )


def downgrade() -> None:
    op.drop_column("users", "hashed_password")
