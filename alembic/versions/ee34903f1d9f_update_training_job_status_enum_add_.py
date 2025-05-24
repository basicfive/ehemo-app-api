"""update_training_job_status_enum_add_thumbnail_states

Revision ID: ee34903f1d9f
Revises: eb64a86f0afc
Create Date: 2025-05-25 03:01:43.568035

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ee34903f1d9f'
down_revision: Union[str, None] = 'eb64a86f0afc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # TrainingJobStatus enum에 새로운 값 추가
    op.execute("ALTER TYPE trainingjobstatus ADD VALUE 'THUMBNAIL_GENERATING'")
    op.execute("ALTER TYPE trainingjobstatus ADD VALUE 'THUMBNAIL_UPSCALING'")


def downgrade() -> None:
    # PostgreSQL에서는 enum 값을 직접 제거할 수 없으므로
    # 필요시 새로운 enum 타입을 생성하고 변경해야 함
    # 현재는 간단히 pass로 처리
    pass
