"""Add streak week feature

Revision ID: 26dde60713d0
Revises: b7ae8dfa93c3
Create Date: 2024-07-24 02:55:25.152935

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '26dde60713d0'
down_revision: Union[str, None] = 'b7ae8dfa93c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('streaks', sa.Column('week', sa.JSON(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('streaks', 'week')
    # ### end Alembic commands ###