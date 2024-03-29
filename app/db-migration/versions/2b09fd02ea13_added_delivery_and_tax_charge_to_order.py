"""added delivery and tax charge to order

Revision ID: 2b09fd02ea13
Revises: 644bb79fa316
Create Date: 2021-04-29 09:53:28.771183

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2b09fd02ea13'
down_revision = '644bb79fa316'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order', sa.Column('delivery_charge', sa.Float(), nullable=True))
    op.add_column('order', sa.Column('tax_charge', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('order', 'tax_charge')
    op.drop_column('order', 'delivery_charge')
    # ### end Alembic commands ###
