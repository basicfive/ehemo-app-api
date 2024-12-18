"""merge heads

Revision ID: 1104f82385f9
Revises: 6f1a2a6e6e1c, 9d3f03e9f9cb
Create Date: 2024-12-18 13:06:50.538197

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1104f82385f9'
down_revision: Union[str, None] = ('6f1a2a6e6e1c', '9d3f03e9f9cb')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
