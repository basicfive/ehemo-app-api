"""added field notification status to generation_request

Revision ID: bed8c0c133e4
Revises: 3c92a5d9dd98
Create Date: 2024-10-31 17:49:23.972225

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bed8c0c133e4'
down_revision: Union[str, None] = '3c92a5d9dd98'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('generation_request', sa.Column('notification_status', sa.Enum('PENDING', 'SUCCESS_NOTIFIED', 'FAILURE_NOTIFIED', name='notificationstatus'), nullable=True))
    op.alter_column('image_generation_job', 's3_key',
               existing_type=sa.VARCHAR(length=1024),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('image_generation_job', 's3_key',
               existing_type=sa.VARCHAR(length=1024),
               nullable=True)
    op.drop_column('generation_request', 'notification_status')
    # ### end Alembic commands ###
