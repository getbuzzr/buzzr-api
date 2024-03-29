"""make department/categroy have order

Revision ID: 54f167789120
Revises: fee22ff8a32c
Create Date: 2021-06-24 15:25:33.065032

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '54f167789120'
down_revision = 'fee22ff8a32c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('category', sa.Column('order', sa.Integer(), nullable=True))
    op.add_column('department', sa.Column('order', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('department', 'order')
    op.drop_column('category', 'order')
    # ### end Alembic commands ###
