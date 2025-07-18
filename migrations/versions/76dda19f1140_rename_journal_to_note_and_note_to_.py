"""Rename journal to note and note to backlog

Revision ID: 76dda19f1140
Revises: 58f525cb1704
Create Date: 2025-07-18 12:02:16.208617

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '76dda19f1140'
down_revision: Union[str, None] = '58f525cb1704'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('backlogs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('date', sa.Date(), nullable=True),
    sa.Column('detail', sa.String(), nullable=True),
    sa.Column('order', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_backlogs_id'), 'backlogs', ['id'], unique=False)
    op.drop_index('ix_journals_id', table_name='journals')
    op.drop_table('journals')
    op.add_column('notes', sa.Column('subject', sa.String(), nullable=True))
    op.add_column('notes', sa.Column('entry', sa.String(), nullable=True))
    op.drop_column('notes', 'detail')
    op.drop_column('notes', 'order')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('notes', sa.Column('order', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('notes', sa.Column('detail', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('notes', 'entry')
    op.drop_column('notes', 'subject')
    op.create_table('journals',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('date', sa.DATE(), autoincrement=False, nullable=True),
    sa.Column('subject', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('entry', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='journals_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='journals_pkey')
    )
    op.create_index('ix_journals_id', 'journals', ['id'], unique=False)
    op.drop_index(op.f('ix_backlogs_id'), table_name='backlogs')
    op.drop_table('backlogs')
    # ### end Alembic commands ###
