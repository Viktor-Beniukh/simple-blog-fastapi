"""Added relationship field to Comment model & Post model

Revision ID: a942c98d393a
Revises: 90106f0f6413
Create Date: 2023-08-29 15:19:42.374074

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a942c98d393a'
down_revision: Union[str, None] = '90106f0f6413'
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
