"""added poster path

Revision ID: 1d139b5c60de
Revises: cc3f8bdde08f
Create Date: 2024-11-29 20:18:55.882304

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1d139b5c60de'
down_revision = 'cc3f8bdde08f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('movies', schema=None) as batch_op:
        batch_op.add_column(sa.Column('poster_path', sa.String(length=300), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('movies', schema=None) as batch_op:
        batch_op.drop_column('poster_path')

    # ### end Alembic commands ###
