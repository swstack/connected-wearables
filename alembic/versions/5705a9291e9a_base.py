"""base

Revision ID: 5705a9291e9a
Revises: None
Create Date: 2014-06-14 16:38:45.704819

"""

# revision identifiers, used by Alembic.
revision = '5705a9291e9a'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('password', sa.String(), nullable=True),
    sa.Column('admin', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('dcaccount',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('password', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('hapiaccount',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('app_key', sa.String(), nullable=True),
    sa.Column('client_id', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('syncstate',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('endpoint', sa.String(), nullable=True),
    sa.Column('hapiaccount_id', sa.Integer(), nullable=True),
    sa.Column('last_sync_time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['hapiaccount_id'], ['hapiaccount.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('cwearapplication',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('owner', sa.Integer(), nullable=False),
    sa.Column('dcaccount', sa.Integer(), nullable=True),
    sa.Column('hapiaccount', sa.Integer(), nullable=True),
    sa.Column('last_sync_time', sa.DateTime(), nullable=True),
    sa.Column('sync_freq_secs', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['dcaccount'], ['dcaccount.id'], ),
    sa.ForeignKeyConstraint(['hapiaccount'], ['hapiaccount.id'], ),
    sa.ForeignKeyConstraint(['owner'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('cwearapplication')
    op.drop_table('syncstate')
    op.drop_table('hapiaccount')
    op.drop_table('dcaccount')
    op.drop_table('users')
    ### end Alembic commands ###