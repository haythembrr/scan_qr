"""empty message

Revision ID: 5864d25fc2aa
Revises: f775be74f32c
Create Date: 2023-06-26 21:11:57.188886

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5864d25fc2aa'
down_revision = 'f775be74f32c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('roles_users')
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('role',
               existing_type=sa.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('role',
               existing_type=sa.INTEGER(),
               nullable=False)

    op.create_table('roles_users',
    sa.Column('users_id', sa.INTEGER(), nullable=True),
    sa.Column('role_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], name='fk_roles_users_role_id_role'),
    sa.ForeignKeyConstraint(['users_id'], ['user.id'], name='fk_roles_users_users_id_user')
    )
    # ### end Alembic commands ###
