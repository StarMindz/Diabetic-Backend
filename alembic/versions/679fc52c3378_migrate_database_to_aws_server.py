"""Migrate database to AWS server

Revision ID: 679fc52c3378
Revises: c5c2de4150da
Create Date: 2024-08-29 14:31:56.322145

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '679fc52c3378'
down_revision: Union[str, None] = 'c5c2de4150da'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###