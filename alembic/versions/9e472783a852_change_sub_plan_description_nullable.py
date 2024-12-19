"""(change) sub plan description nullable

Revision ID: 9e472783a852
Revises: e856e5aa0edf
Create Date: 2024-12-19 16:41:39.826246

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9e472783a852'
down_revision: Union[str, None] = 'e856e5aa0edf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('subscription_plan', 'description',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('subscription_plan', 'description',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###
