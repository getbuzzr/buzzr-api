"""change to date_prepared

Revision ID: a26fa7fe84ff
Revises: e910b4e661be
Create Date: 2021-05-11 10:54:42.466673

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'a26fa7fe84ff'
down_revision = 'e910b4e661be'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order', sa.Column('date_preparing', sa.DateTime(), nullable=True))
    op.drop_column('order', 'date_prepared')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order', sa.Column('date_prepared', mysql.DATETIME(), nullable=True))
    op.drop_column('order', 'date_preparing')
    # ### end Alembic commands ###
