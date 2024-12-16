"""(add) versioning table - app version

Revision ID: 9d3f03e9f9cb
Revises: 1566ee61c2eb
Create Date: 2024-12-16 05:01:19.714527

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9d3f03e9f9cb'
down_revision: Union[str, None] = '1566ee61c2eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('app_version',
    sa.Column('platform', sa.Enum('IOS', 'ANDROID', name='platformenum'), nullable=False),
    sa.Column('min_version', sa.String(), nullable=False),
    sa.Column('latest_version', sa.String(), nullable=False),
    sa.Column('store_url', sa.String(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('app_version')
    # ### end Alembic commands ###
