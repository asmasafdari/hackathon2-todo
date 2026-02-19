"""Add priority, tags, due_date, remind_at, recurrence fields to todos

Revision ID: 003_add_priority_tags_duedate_recurrence
Revises: 002_add_hashed_password
Create Date: 2026-02-17

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = "003_add_priority_tags_duedate_recurrence"
down_revision: Union[str, None] = "002_add_hashed_password"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "todos",
        sa.Column(
            "priority",
            sa.String(length=10),
            nullable=True,
        ),
    )
    op.add_column(
        "todos",
        sa.Column("tags", sa.JSON(), nullable=True),
    )
    op.add_column(
        "todos",
        sa.Column("due_date", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "todos",
        sa.Column("remind_at", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "todos",
        sa.Column("recurrence_rule", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "todos",
        sa.Column("recurrence_parent_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
    )
    op.create_foreign_key(
        "fk_todos_recurrence_parent",
        "todos",
        "todos",
        ["recurrence_parent_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_todos_recurrence_parent", "todos", type_="foreignkey")
    op.drop_column("todos", "recurrence_parent_id")
    op.drop_column("todos", "recurrence_rule")
    op.drop_column("todos", "remind_at")
    op.drop_column("todos", "due_date")
    op.drop_column("todos", "tags")
    op.drop_column("todos", "priority")
