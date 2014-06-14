"""create user table

Revision ID: 5240cdd2c8aa
Revises: None
Create Date: 2014-06-13 22:50:38.029331

"""

# revision identifiers, used by Alembic.
revision = '5240cdd2c8aa'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'user',
        sa.Column('id', sa.INTEGER),
        sa.Column('name', sa.TEXT),
        sa.Column('password', sa.TEXT),
        sa.Column('admin', sa.BOOLEAN)
    )


def downgrade():
    op.drop_table('user')
