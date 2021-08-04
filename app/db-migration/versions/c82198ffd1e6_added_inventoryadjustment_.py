"""Added InventoryAdjustment ProductPurchased tables  and sale tax and percent discount columns to ProductOrdered

Revision ID: c82198ffd1e6
Revises: 10e498b95e5a
Create Date: 2021-07-30 21:48:31.283043

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c82198ffd1e6'
down_revision = '10e498b95e5a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('product_ordered', sa.Column('percent_discount', sa.Integer(), nullable=True))
    op.add_column('product_ordered', sa.Column('sale_price_cents', sa.Integer(), nullable=True))
    op.add_column('product_ordered', sa.Column('tax', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('product_ordered', 'tax')
    op.drop_column('product_ordered', 'sale_price_cents')
    op.drop_column('product_ordered', 'percent_discount')
    # ### end Alembic commands ###
