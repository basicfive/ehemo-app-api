"""add_new_enum_values_to_token_types

Revision ID: 30aa88cacd47
Revises: 327b0da99889
Create Date: 2025-08-29 01:36:58.386183

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '30aa88cacd47'
down_revision: Union[str, None] = '327b0da99889'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new enum values to TokenTransactionType (only DEPOSIT is new)
    op.execute("ALTER TYPE tokentransactiontype ADD VALUE 'DEPOSIT'")
    
    # Add new enum values to TokenSourceType (only STORE_PURCHASE is new)
    op.execute("ALTER TYPE tokensourcetype ADD VALUE 'STORE_PURCHASE'")


def downgrade() -> None:
    # PostgreSQL doesn't support removing enum values directly
    # Manual intervention required to remove enum values
    pass
