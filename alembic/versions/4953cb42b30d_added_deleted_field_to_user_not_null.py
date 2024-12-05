"""added deleted field to user - not null

Revision ID: 4953cb42b30d
Revises: cb9716fecf9f
Create Date: 2024-12-02 09:30:52.544135

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4953cb42b30d'
down_revision: Union[str, None] = 'cb9716fecf9f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'deleted',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'deleted',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    # ### end Alembic commands ###