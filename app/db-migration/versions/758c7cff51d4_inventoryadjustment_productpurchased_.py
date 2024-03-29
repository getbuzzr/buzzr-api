"""InventoryAdjustment ProductPurchased added

Revision ID: 758c7cff51d4
Revises: c82198ffd1e6
Create Date: 2021-08-04 16:46:39.512541

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '758c7cff51d4'
down_revision = 'c82198ffd1e6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('inventory_adjustment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.SmallInteger(), nullable=True),
    sa.Column('date_adjusted', sa.DateTime(), nullable=True),
    sa.Column('product_id', sa.Integer(), nullable=True),
    sa.Column('reason', sa.Enum('spoilage', 'damage', 'inventory_error', 'theft', 'delivery_error', 'writeoff', name='adjustmentreason'), nullable=True),
    sa.ForeignKeyConstraint(['product_id'], ['product.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('product_purchased',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.SmallInteger(), nullable=True),
    sa.Column('date_purchased', sa.DateTime(), nullable=True),
    sa.Column('product_id', sa.Integer(), nullable=True),
    sa.Column('purchase_price_cents', sa.Integer(), nullable=True),
    sa.Column('tax', sa.Float(), nullable=True),
    sa.Column('date_expiry', sa.DateTime(), nullable=True),
    sa.Column('location_purchased', sa.String(length=200), nullable=True),
    sa.ForeignKeyConstraint(['product_id'], ['product.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('product_purchased')
    op.drop_table('inventory_adjustment')
    # ### end Alembic commands ###
