"""empty message

Revision ID: 966db79107be
Revises: fea6ad4bdb7f
Create Date: 2023-06-25 21:21:58.754618

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '966db79107be'
down_revision = 'fea6ad4bdb7f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.add_column(sa.Column('title', sa.String(length=255), nullable=False))
        batch_op.add_column(sa.Column('content', sa.Text(), nullable=False))
        batch_op.add_column(sa.Column('author_id', sa.Integer(), nullable=False))
        batch_op.drop_index('ix_post_timestamp')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(None, 'user', ['author_id'], ['id'])
        batch_op.drop_column('body')
        batch_op.drop_column('timestamp')
        batch_op.drop_column('user_id')

    with op.batch_alter_table('role', schema=None) as batch_op:
        batch_op.add_column(sa.Column('description', sa.Text(), nullable=False))
        batch_op.drop_column('desc')

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('role_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(None, 'role', ['role_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('role_id')

    with op.batch_alter_table('role', schema=None) as batch_op:
        batch_op.add_column(sa.Column('desc', sa.VARCHAR(length=180), nullable=True))
        batch_op.drop_column('description')

    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column('timestamp', sa.DATETIME(), nullable=True))
        batch_op.add_column(sa.Column('body', sa.VARCHAR(length=140), nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['id'])
        batch_op.create_index('ix_post_timestamp', ['timestamp'], unique=False)
        batch_op.drop_column('author_id')
        batch_op.drop_column('content')
        batch_op.drop_column('title')

    # ### end Alembic commands ###