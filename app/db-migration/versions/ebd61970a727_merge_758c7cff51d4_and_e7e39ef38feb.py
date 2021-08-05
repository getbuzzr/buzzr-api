"""merge 758c7cff51d4 and e7e39ef38feb

Revision ID: ebd61970a727
Revises: e7e39ef38feb, 758c7cff51d4
Create Date: 2021-08-04 17:34:46.506493

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ebd61970a727'
down_revision = ('e7e39ef38feb', '758c7cff51d4')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
