"""added fcm_token field to user

Revision ID: 969d1d6d5926
Revises: 7c194ccf089d
Create Date: 2024-12-04 10:16:23.420758

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '969d1d6d5926'
down_revision: Union[str, None] = '7c194ccf089d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('fcm_token', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'fcm_token')
    # ### end Alembic commands ###