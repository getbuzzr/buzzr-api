"""add servings/calories

Revision ID: 10e498b95e5a
Revises: 265400bbf6b9
Create Date: 2021-07-03 10:57:40.498221

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '10e498b95e5a'
down_revision = '265400bbf6b9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('recipe', sa.Column('active_time_seconds', sa.Integer(), nullable=True))
    op.add_column('recipe', sa.Column('calories', sa.Integer(), nullable=True))
    op.add_column('recipe', sa.Column('instructions', sa.Text(), nullable=True))
    op.add_column('recipe', sa.Column('servings', sa.Integer(), nullable=True))
    op.add_column('recipe', sa.Column('total_time_seconds', sa.Integer(), nullable=True))
    op.drop_column('recipe', 'cooking_time_seconds')
    op.drop_column('recipe', 'preparation_time_seconds')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('recipe', sa.Column('preparation_time_seconds', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.add_column('recipe', sa.Column('cooking_time_seconds', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.drop_column('recipe', 'total_time_seconds')
    op.drop_column('recipe', 'servings')
    op.drop_column('recipe', 'instructions')
    op.drop_column('recipe', 'calories')
    op.drop_column('recipe', 'active_time_seconds')
    # ### end Alembic commands ###
