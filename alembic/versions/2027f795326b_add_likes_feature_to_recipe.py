"""add likes feature to recipe

Revision ID: 2027f795326b
Revises: 22d241b01b1b
Create Date: 2024-08-02 14:51:52.354363

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2027f795326b'
down_revision: Union[str, None] = '22d241b01b1b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('recipes', sa.Column('total_likes', sa.Float(), nullable=False, server_default='0'))
    op.add_column('recipes', sa.Column('liked_by', sa.JSON(), nullable=False, server_default='[]'))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('recipes', 'liked_by')
    op.drop_column('recipes', 'total_likes')
    # ### end Alembic commands ###
