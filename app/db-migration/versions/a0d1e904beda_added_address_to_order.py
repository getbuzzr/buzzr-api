"""added address to order

Revision ID: a0d1e904beda
Revises: 8cd0ce3bdab2
Create Date: 2021-04-12 22:57:03.343044

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a0d1e904beda'
down_revision = '8cd0ce3bdab2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order', sa.Column('address_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'order', 'address', ['address_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'order', type_='foreignkey')
    op.drop_column('order', 'address_id')
    # ### end Alembic commands ###
