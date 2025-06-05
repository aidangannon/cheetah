"""change_layout_coordinates_to_array

Revision ID: 59de50678d81
Revises: 1260f63e32b1
Create Date: 2025-08-19 23:58:14.895800

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '59de50678d81'
down_revision: Union[str, Sequence[str], None] = '1260f63e32b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add the new coordinates column as JSON
    op.add_column('view_configs', sa.Column('coordinates', sa.JSON(), nullable=True))
    
    # Migrate existing data: combine x, y, w, h into coordinates array (PostgreSQL syntax)
    op.execute("""
        UPDATE view_configs 
        SET coordinates = json_build_array(x, y, w, h)
        WHERE x IS NOT NULL AND y IS NOT NULL AND w IS NOT NULL AND h IS NOT NULL
    """)
    
    # Drop the old columns
    op.drop_column('view_configs', 'h')
    op.drop_column('view_configs', 'w')
    op.drop_column('view_configs', 'y')
    op.drop_column('view_configs', 'x')


def downgrade() -> None:
    """Downgrade schema."""
    # Add back the individual columns
    op.add_column('view_configs', sa.Column('x', sa.INTEGER(), nullable=True))
    op.add_column('view_configs', sa.Column('y', sa.INTEGER(), nullable=True))
    op.add_column('view_configs', sa.Column('w', sa.INTEGER(), nullable=True))
    op.add_column('view_configs', sa.Column('h', sa.INTEGER(), nullable=True))
    
    # Migrate data back from coordinates array to individual columns (PostgreSQL syntax)
    op.execute("""
        UPDATE view_configs 
        SET x = (coordinates->>0)::integer,
            y = (coordinates->>1)::integer,
            w = (coordinates->>2)::integer,
            h = (coordinates->>3)::integer
        WHERE coordinates IS NOT NULL
    """)
    
    # Drop the coordinates column
    op.drop_column('view_configs', 'coordinates')
