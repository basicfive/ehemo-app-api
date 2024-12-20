"""changed generation request field - notification status -> generation result

Revision ID: 2e3ac4ffae48
Revises: 9caad7eec161
Create Date: 2024-11-25 09:34:28.550276

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2e3ac4ffae48'
down_revision: Union[str, None] = '9caad7eec161'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    # 먼저 Enum 타입을 생성
    generation_result_enum = sa.Enum('PENDING', 'SUCCEED', 'FAILED', 'CANCELED',
                                     name='generationresultenum')
    generation_result_enum.create(op.get_bind())

    op.add_column('generation_request', sa.Column('generation_result', sa.Enum('PENDING', 'SUCCEED', 'FAILED', 'CANCELED', name='generationresultenum'), nullable=True))
    op.drop_column('generation_request', 'notification_status')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('generation_request', sa.Column('notification_status', postgresql.ENUM('PENDING', 'SUCCESS_NOTIFIED', 'FAILURE_NOTIFIED', name='notificationstatus'), autoincrement=False, nullable=False))
    op.drop_column('generation_request', 'generation_result')
    # ### end Alembic commands ###
    # Enum 타입 삭제
    sa.Enum(name='generationresultenum').drop(op.get_bind())

