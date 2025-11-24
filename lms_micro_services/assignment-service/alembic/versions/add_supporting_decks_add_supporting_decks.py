"""Add supporting_decks columns to assignments

Revision ID: add_supporting_decks
Revises: 029f533245ae
Create Date: 2025-10-14 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_supporting_decks'
down_revision: Union[str, Sequence[str], None] = '029f533245ae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add supporting_decks and supporting_deck_titles columns"""
    op.add_column('assignments', sa.Column('supporting_decks', sa.Text(), nullable=True))
    op.add_column('assignments', sa.Column('supporting_deck_titles', sa.Text(), nullable=True))


def downgrade() -> None:
    """Remove supporting_decks and supporting_deck_titles columns"""
    op.drop_column('assignments', 'supporting_deck_titles')
    op.drop_column('assignments', 'supporting_decks')
