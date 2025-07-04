"""Remove trial tracking attributes from User table

Revision ID: 257b37003e5d
Revises: ddc4ec7800bc
Create Date: 2025-04-18 09:30:45.483630

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "257b37003e5d"
down_revision: Union[str, None] = "ddc4ec7800bc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "trial_end")
    op.drop_column("users", "trial_start")
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "users",
        sa.Column(
            "trial_start", postgresql.TIMESTAMP(), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "trial_end", postgresql.TIMESTAMP(), autoincrement=False, nullable=True
        ),
    )
    # ### end Alembic commands ###
