"""add overview to movie table

Revision ID: 2047b32461a2
Revises: 1d139b5c60de
Create Date: 2024-11-29 21:41:54.731071

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2047b32461a2'
down_revision = '1d139b5c60de'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('movies', schema=None) as batch_op:
        batch_op.add_column(sa.Column('overview', sa.Text(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('movies', schema=None) as batch_op:
        batch_op.drop_column('overview')

    # ### end Alembic commands ###
