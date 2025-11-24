"""Change content_type and status from ENUM to VARCHAR

Revision ID: change_enum_to_varchar
Revises: add_supporting_decks
Create Date: 2025-10-14 17:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'change_enum_to_varchar'
down_revision: Union[str, Sequence[str], None] = 'add_supporting_decks'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Change content_type and status from ENUM to VARCHAR"""
    
    # Change content_type from ENUM to VARCHAR
    op.execute("ALTER TABLE assignments ALTER COLUMN content_type TYPE VARCHAR(20) USING content_type::text")
    
    # Change status from ENUM to VARCHAR
    op.execute("ALTER TABLE assignments ALTER COLUMN status TYPE VARCHAR(20) USING status::text")
    
    # Drop the ENUM types
    op.execute("DROP TYPE IF EXISTS contenttype")
    op.execute("DROP TYPE IF EXISTS assignmentstatus")


def downgrade() -> None:
    """Change content_type and status back to ENUM"""
    
    # Recreate ENUM types
    op.execute("CREATE TYPE contenttype AS ENUM ('COURSE', 'DECK')")
    op.execute("CREATE TYPE assignmentstatus AS ENUM ('PENDING', 'IN_PROGRESS', 'COMPLETED', 'OVERDUE')")
    
    # Change columns back to ENUM
    op.execute("ALTER TABLE assignments ALTER COLUMN content_type TYPE contenttype USING content_type::contenttype")
    op.execute("ALTER TABLE assignments ALTER COLUMN status TYPE assignmentstatus USING status::assignmentstatus")
