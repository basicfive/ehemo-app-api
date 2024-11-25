"""changed generation request field - notification status -> generation result - not null

Revision ID: 938e314f5972
Revises: 2e3ac4ffae48
Create Date: 2024-11-25 09:44:53.491259

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '938e314f5972'
down_revision: Union[str, None] = '2e3ac4ffae48'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('generation_request', 'generation_result',
               existing_type=postgresql.ENUM('PENDING', 'SUCCEED', 'FAILED', 'CANCELED', name='generationresultenum'),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('generation_request', 'generation_result',
               existing_type=postgresql.ENUM('PENDING', 'SUCCEED', 'FAILED', 'CANCELED', name='generationresultenum'),
               nullable=True)
    # ### end Alembic commands ###
