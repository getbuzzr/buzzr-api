"""add search_term

Revision ID: fee22ff8a32c
Revises: 720737587a45
Create Date: 2021-06-23 16:59:34.717570

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fee22ff8a32c'
down_revision = '720737587a45'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('product', sa.Column('search_term', sa.String(length=100), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('product', 'search_term')
    # ### end Alembic commands ###
