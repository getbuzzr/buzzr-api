"""added approx weight

Revision ID: a29acfdda9e3
Revises: 9421151ba04f
Create Date: 2021-06-07 22:23:41.564864

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = 'a29acfdda9e3'
down_revision = '9421151ba04f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    conn = op.get_bind()
    conn.execute(
        text(
            """
    ALTER TABLE `product` MODIFY `product`.`unit` ENUM(
        'weight', 
        'pack', 
        'volume', 
        'piece',
        'approx_weight'
        )
        """
        ))
    pass
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
