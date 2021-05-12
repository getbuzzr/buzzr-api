"""added order/address status so we dont hard delete

Revision ID: 904c91adc946
Revises: a26fa7fe84ff
Create Date: 2021-05-12 10:02:12.816867

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '904c91adc946'
down_revision = 'a26fa7fe84ff'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('address', sa.Column('status', sa.Enum('active', 'deleted', name='addressstatusenum'), server_default='active', nullable=True))
    op.add_column('product', sa.Column('status', sa.Enum('active', 'deleted', 'hidden', name='productstatusenum'), server_default='active', nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('product', 'status')
    op.drop_column('address', 'status')
    # ### end Alembic commands ###
