"""(add) subscription & token table

Revision ID: f2e8f573f91f
Revises: 1104f82385f9
Create Date: 2024-12-18 13:07:15.444268

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f2e8f573f91f'
down_revision: Union[str, None] = '1104f82385f9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_subscription_original_transaction_id', table_name='subscription')
    op.drop_index('ix_subscription_user_id', table_name='subscription')
    op.drop_table('subscription')
    op.add_column('store_product', sa.Column('store_type', sa.Enum('APP_STORE', 'PLAY_STORE', name='storetype'), nullable=True))
    op.add_column('store_product', sa.Column('product_id', sa.String(), nullable=True))
    op.add_column('store_product', sa.Column('subscription_plan_id', sa.Integer(), nullable=False))
    op.create_unique_constraint('uix_plan_store', 'store_product', ['subscription_plan_id', 'store_type'])
    op.create_foreign_key(None, 'store_product', 'subscription_plan', ['subscription_plan_id'], ['id'])
    op.add_column('subscription_plan', sa.Column('name', sa.String(), nullable=False))
    op.add_column('subscription_plan', sa.Column('description', sa.String(), nullable=False))
    op.add_column('subscription_plan', sa.Column('plan_type', sa.Enum('FREE', 'STANDARD', 'PREMIUM', name='subscriptionplantype'), nullable=False))
    op.add_column('subscription_plan', sa.Column('billing_interval', sa.Enum('MONTHLY', 'YEARLY', name='billinginterval'), nullable=True))
    op.add_column('subscription_plan', sa.Column('tokens_per_period', sa.Integer(), nullable=False))
    op.add_column('subscription_plan', sa.Column('base_price', sa.Float(), nullable=False))
    op.add_column('subscription_plan', sa.Column('discount_rate', sa.Float(), nullable=False))
    op.add_column('subscription_plan', sa.Column('final_price', sa.Float(), nullable=False))
    op.add_column('subscription_plan', sa.Column('has_discount', sa.Boolean(), nullable=False))
    op.add_column('subscription_plan', sa.Column('discount_description', sa.String(), nullable=True))
    op.add_column('user_subscription', sa.Column('latest_transaction_id', sa.String(length=50), nullable=True))
    op.add_column('user_subscription', sa.Column('purchase_date', sa.DateTime(), nullable=False))
    op.add_column('user_subscription', sa.Column('auto_renew_status', sa.Boolean(), nullable=False))
    op.add_column('user_subscription', sa.Column('canceled_at', sa.DateTime(), nullable=True))
    op.add_column('user_subscription', sa.Column('store_product_id', sa.Integer(), nullable=False))
    op.alter_column('user_subscription', 'original_transaction_id',
               existing_type=sa.VARCHAR(length=50),
               nullable=False)
    op.alter_column('user_subscription', 'expire_date',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=sa.DateTime(),
               existing_nullable=False)
    op.create_index('idx_subscription_status_expire', 'user_subscription', ['status', 'expire_date'], unique=False)
    op.create_index(op.f('ix_user_subscription_status'), 'user_subscription', ['status'], unique=False)
    op.create_index(op.f('ix_user_subscription_store_product_id'), 'user_subscription', ['store_product_id'], unique=True)
    op.create_foreign_key(None, 'user_subscription', 'store_product', ['store_product_id'], ['id'])
    op.drop_column('user_subscription', 'next_token_refill_date')
    op.drop_column('user_subscription', 'store')
    op.drop_column('user_subscription', 'timezone')
    op.drop_column('user_subscription', 'billing_interval')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_subscription', sa.Column('billing_interval', postgresql.ENUM('MONTHLY', 'YEARLY', name='billinginterval'), autoincrement=False, nullable=True))
    op.add_column('user_subscription', sa.Column('timezone', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('user_subscription', sa.Column('store', postgresql.ENUM('APP_STORE', 'PLAY_STORE', name='storetype'), autoincrement=False, nullable=True))
    op.add_column('user_subscription', sa.Column('next_token_refill_date', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'user_subscription', type_='foreignkey')
    op.drop_index(op.f('ix_user_subscription_store_product_id'), table_name='user_subscription')
    op.drop_index(op.f('ix_user_subscription_status'), table_name='user_subscription')
    op.drop_index('idx_subscription_status_expire', table_name='user_subscription')
    op.alter_column('user_subscription', 'expire_date',
               existing_type=sa.DateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=False)
    op.alter_column('user_subscription', 'original_transaction_id',
               existing_type=sa.VARCHAR(length=50),
               nullable=True)
    op.drop_column('user_subscription', 'store_product_id')
    op.drop_column('user_subscription', 'canceled_at')
    op.drop_column('user_subscription', 'auto_renew_status')
    op.drop_column('user_subscription', 'purchase_date')
    op.drop_column('user_subscription', 'latest_transaction_id')
    op.drop_column('subscription_plan', 'discount_description')
    op.drop_column('subscription_plan', 'has_discount')
    op.drop_column('subscription_plan', 'final_price')
    op.drop_column('subscription_plan', 'discount_rate')
    op.drop_column('subscription_plan', 'base_price')
    op.drop_column('subscription_plan', 'tokens_per_period')
    op.drop_column('subscription_plan', 'billing_interval')
    op.drop_column('subscription_plan', 'plan_type')
    op.drop_column('subscription_plan', 'description')
    op.drop_column('subscription_plan', 'name')
    op.drop_constraint(None, 'store_product', type_='foreignkey')
    op.drop_constraint('uix_plan_store', 'store_product', type_='unique')
    op.drop_column('store_product', 'subscription_plan_id')
    op.drop_column('store_product', 'product_id')
    op.drop_column('store_product', 'store_type')
    op.create_table('subscription',
    sa.Column('original_transaction_id', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
    sa.Column('store', postgresql.ENUM('APP_STORE', 'PLAY_STORE', name='storetype'), autoincrement=False, nullable=True),
    sa.Column('token', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('timezone', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('next_token_refill_date', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('expire_date', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('plan_type', postgresql.ENUM('FREE', 'STANDARD', 'PREMIUM', name='subscriptionplantype'), autoincrement=False, nullable=False),
    sa.Column('billing_interval', postgresql.ENUM('MONTHLY', 'YEARLY', name='billinginterval'), autoincrement=False, nullable=True),
    sa.Column('status', postgresql.ENUM('ACTIVE', 'EXPIRED', 'CANCELED', 'PENDING', 'TRIAL', name='subscriptionstatus'), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='subscription_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='subscription_pkey')
    )
    op.create_index('ix_subscription_user_id', 'subscription', ['user_id'], unique=True)
    op.create_index('ix_subscription_original_transaction_id', 'subscription', ['original_transaction_id'], unique=True)
    # ### end Alembic commands ###
