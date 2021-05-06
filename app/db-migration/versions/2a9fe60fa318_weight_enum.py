"""weight/enum

Revision ID: 2a9fe60fa318
Revises: 81e0af633cdb
Create Date: 2021-05-06 16:34:12.636268

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '2a9fe60fa318'
down_revision = '81e0af633cdb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('product', sa.Column('quantity', sa.Integer(), nullable=True))
    op.add_column('product', sa.Column('unit', sa.Enum('weight', 'pack', 'volume', 'piece', name='productunitenum'), server_default='weight', nullable=True))
    op.drop_column('product', 'quantity_per_order')
    op.drop_column('product', 'weight')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('product', sa.Column('weight', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.add_column('product', sa.Column('quantity_per_order', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.drop_column('product', 'unit')
    op.drop_column('product', 'quantity')
    # ### end Alembic commands ###
