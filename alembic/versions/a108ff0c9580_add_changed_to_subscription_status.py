"""add_changed_to_subscription_status

Revision ID: a108ff0c9580
Revises: 26ece0c88c94
Create Date: 2025-01-02 17:44:02.539950

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a108ff0c9580'
down_revision: Union[str, None] = '26ece0c88c94'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# 기존 enum 값들
old_status = ['ACTIVE', 'EXPIRED', 'CANCELED', 'PENDING', 'TRIAL']
# 새로운 enum 값들 (CHANGED 추가)
new_status = ['ACTIVE', 'EXPIRED', 'CANCELED', 'PENDING', 'CHANGED', 'TRIAL']


def upgrade():
    # 1. status 컬럼을 임시로 문자열로 변경
    op.execute("ALTER TABLE user_subscription ALTER COLUMN status TYPE VARCHAR USING status::VARCHAR")

    # 2. 기존 enum 타입 삭제
    op.execute("DROP TYPE subscriptionstatus")

    # 3. 새로운 enum 타입 생성
    op.execute(
        "CREATE TYPE subscriptionstatus AS ENUM ('ACTIVE', 'EXPIRED', 'CANCELED', 'PENDING', 'CHANGED', 'TRIAL')")

    # 4. 컬럼을 새로운 enum 타입으로 변경
    op.execute(
        "ALTER TABLE user_subscription ALTER COLUMN status TYPE subscriptionstatus USING status::subscriptionstatus")


def downgrade():
    # 1. status 컬럼을 임시로 문자열로 변경
    op.execute("ALTER TABLE user_subscription ALTER COLUMN status TYPE VARCHAR USING status::VARCHAR")

    # 2. 기존 enum 타입 삭제
    op.execute("DROP TYPE subscriptionstatus")

    # 3. 이전 enum 타입 재생성
    op.execute("CREATE TYPE subscriptionstatus AS ENUM ('ACTIVE', 'EXPIRED', 'CANCELED', 'PENDING', 'TRIAL')")

    # 4. 컬럼을 이전 enum 타입으로 변경
    op.execute(
        "ALTER TABLE user_subscription ALTER COLUMN status TYPE subscriptionstatus USING status::subscriptionstatus")