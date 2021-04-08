"""added new enum type

Revision ID: 1e33396e2700
Revises: 82aa4bfcd72d
Create Date: 2021-04-07 15:47:09.793049

"""
from sqlalchemy.sql import text
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1e33396e2700'
down_revision = '82aa4bfcd72d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    conn = op.get_bind()
    conn.execute(
        text(
            """
    ALTER TABLE `order` MODIFY `order`.`status` ENUM(
        'checking_out',
        'failed',
        'paid',
        'preparing',
        'delivered',
        'complete',
        'arrived')
        """
        ))
    pass
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
