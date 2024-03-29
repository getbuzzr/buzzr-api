"""added rider

Revision ID: fba68dd9daae
Revises: 7f3e810443a3
Create Date: 2021-05-27 13:54:21.210034

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fba68dd9daae'
down_revision = '7f3e810443a3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('rider',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('cognito_sub', sa.String(length=36), nullable=True),
    sa.Column('email', sa.String(length=50), nullable=False),
    sa.Column('first_name', sa.String(length=100), nullable=True),
    sa.Column('last_name', sa.String(length=100), nullable=True),
    sa.Column('phone_number', sa.String(length=20), nullable=True),
    sa.Column('phone_country_code', sa.String(length=5), nullable=True),
    sa.Column('date_created', sa.DateTime(), nullable=True),
    sa.Column('last_login', sa.DateTime(), nullable=True),
    sa.Column('apn_token', sa.String(length=100), nullable=True),
    sa.Column('fcm_token', sa.String(length=100), nullable=True),
    sa.Column('profile_picture_url', sa.String(length=400), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.add_column('order', sa.Column('rider_assigned_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'order', 'rider', ['rider_assigned_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'order', type_='foreignkey')
    op.drop_column('order', 'rider_assigned_id')
    op.drop_table('rider')
    # ### end Alembic commands ###
