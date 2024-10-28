"""add_user_id_sequence

Revision ID: 856c0494a955
Revises: e72b0ea3787e
Create Date: 2024-10-29 00:44:13.366680

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '856c0494a955'
down_revision: Union[str, None] = 'e72b0ea3787e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.execute("""
        SELECT setval('user_id_seq', (SELECT MAX(id) FROM "user"));
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE "user" ALTER COLUMN id DROP DEFAULT;
        DROP SEQUENCE IF EXISTS user_id_seq;
    """)
