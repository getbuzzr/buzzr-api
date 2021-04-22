"""added popularsearches

Revision ID: 91ae8c96c0f0
Revises: a0d1e904beda
Create Date: 2021-04-19 14:48:47.458014

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '91ae8c96c0f0'
down_revision = 'a0d1e904beda'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('popular_searches',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('popular_searches')
    # ### end Alembic commands ###