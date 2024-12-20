"""changing notification status in generation request to not null

Revision ID: c3d1f0794831
Revises: bed8c0c133e4
Create Date: 2024-10-31 17:54:23.990983

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c3d1f0794831'
down_revision: Union[str, None] = 'bed8c0c133e4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('generation_request', 'notification_status',
               existing_type=postgresql.ENUM('PENDING', 'SUCCESS_NOTIFIED', 'FAILURE_NOTIFIED', name='notificationstatus'),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('generation_request', 'notification_status',
               existing_type=postgresql.ENUM('PENDING', 'SUCCESS_NOTIFIED', 'FAILURE_NOTIFIED', name='notificationstatus'),
               nullable=True)
    # ### end Alembic commands ###
