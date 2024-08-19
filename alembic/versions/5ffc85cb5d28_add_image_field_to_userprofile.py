"""Add image field to UserProfile

Revision ID: 5ffc85cb5d28
Revises: f4da891f3fd6
Create Date: 2024-08-18 19:40:15.517628

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5ffc85cb5d28'
down_revision: Union[str, None] = 'f4da891f3fd6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_profiles', sa.Column('image', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user_profiles', 'image')
    # ### end Alembic commands ###