"""added deleted field to image & image group for soft delete

Revision ID: 6a6233450596
Revises: 856c0494a955
Create Date: 2024-10-30 14:23:37.672636

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6a6233450596'
down_revision: Union[str, None] = '856c0494a955'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('generated_image', sa.Column('deleted', sa.Boolean(), nullable=True))
    op.add_column('generated_image_group', sa.Column('deleted', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('generated_image_group', 'deleted')
    op.drop_column('generated_image', 'deleted')
    # ### end Alembic commands ###
