"""add_transferred_to_subscription_status

Revision ID: 202bb3ce125f
Revises: cb4593e4ff11
Create Date: 2025-01-04 03:13:31.144201

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '202bb3ce125f'
down_revision: Union[str, None] = 'cb4593e4ff11'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    # 1. status 컬럼을 임시로 문자열로 변경
    op.execute("ALTER TABLE user_subscription ALTER COLUMN status TYPE VARCHAR USING status::VARCHAR")

    # 2. 기존 enum 타입 삭제
    op.execute("DROP TYPE subscriptionstatus")

    # 3. 새로운 enum 타입 생성
    op.execute(
        "CREATE TYPE subscriptionstatus AS ENUM ('ACTIVE', 'EXPIRED', 'CANCELED', 'PENDING', 'TRANSFERRED', 'CHANGED', 'TRIAL')")

    # 4. 컬럼을 새로운 enum 타입으로 변경
    op.execute(
        "ALTER TABLE user_subscription ALTER COLUMN status TYPE subscriptionstatus USING status::subscriptionstatus")


def downgrade():
    # 1. status 컬럼을 임시로 문자열로 변경
    op.execute("ALTER TABLE user_subscription ALTER COLUMN status TYPE VARCHAR USING status::VARCHAR")

    # 2. 기존 enum 타입 삭제
    op.execute("DROP TYPE subscriptionstatus")

    # 3. 이전 enum 타입 재생성
    op.execute("CREATE TYPE subscriptionstatus AS ENUM ('ACTIVE', 'EXPIRED', 'CANCELED', 'PENDING', 'CHANGED', 'TRIAL')")

    # 4. 컬럼을 이전 enum 타입으로 변경
    op.execute(
        "ALTER TABLE user_subscription ALTER COLUMN status TYPE subscriptionstatus USING status::subscriptionstatus")
