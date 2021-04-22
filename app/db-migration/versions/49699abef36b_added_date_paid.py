"""added date_paid

Revision ID: 49699abef36b
Revises: e50512287a16
Create Date: 2021-04-22 10:51:30.467777

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '49699abef36b'
down_revision = 'e50512287a16'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order', sa.Column('date_paid', sa.DateTime(), nullable=True))
    op.add_column('product', sa.Column('image_url', sa.String(length=300), nullable=True))
    op.add_column('product', sa.Column('quantity_per_order', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('product', 'quantity_per_order')
    op.drop_column('product', 'image_url')
    op.drop_column('order', 'date_paid')
    # ### end Alembic commands ###