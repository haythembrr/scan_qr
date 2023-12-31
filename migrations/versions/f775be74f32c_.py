"""empty message

Revision ID: f775be74f32c
Revises: cacdcf438024
Create Date: 2023-06-26 20:09:40.811439

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f775be74f32c'
down_revision = 'cacdcf438024'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('machine',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('manufacturer', sa.String(length=64), nullable=True),
    sa.Column('location', sa.String(length=64), nullable=True),
    sa.Column('status', sa.String(length=12), nullable=True),
    sa.Column('install_date', sa.DateTime(), nullable=True),
    sa.Column('comment', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_machine'))
    )
    with op.batch_alter_table('machine', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_machine_install_date'), ['install_date'], unique=False)

    op.create_table('document',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('machine_id', sa.Integer(), nullable=False),
    sa.Column('type', sa.String(length=12), nullable=True),
    sa.Column('upload_date', sa.DateTime(), nullable=True),
    sa.Column('blob', sa.LargeBinary(), nullable=False),
    sa.Column('size', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['machine_id'], ['machine.id'], name=op.f('fk_document_machine_id_machine')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_document'))
    )
    with op.batch_alter_table('document', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_document_upload_date'), ['upload_date'], unique=False)

    op.create_table('intervention',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('machine_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('type', sa.String(length=12), nullable=True),
    sa.Column('comment', sa.String(length=255), nullable=True),
    sa.Column('start_date', sa.DateTime(), nullable=True),
    sa.Column('end_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['machine_id'], ['machine.id'], name=op.f('fk_intervention_machine_id_machine')),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name=op.f('fk_intervention_user_id_user')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_intervention'))
    )
    with op.batch_alter_table('intervention', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_intervention_end_date'), ['end_date'], unique=False)
        batch_op.create_index(batch_op.f('ix_intervention_start_date'), ['start_date'], unique=False)

    with op.batch_alter_table('role', schema=None) as batch_op:
        batch_op.alter_column('description',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.Text(),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('role', schema=None) as batch_op:
        batch_op.alter_column('description',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)

    with op.batch_alter_table('intervention', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_intervention_start_date'))
        batch_op.drop_index(batch_op.f('ix_intervention_end_date'))

    op.drop_table('intervention')
    with op.batch_alter_table('document', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_document_upload_date'))

    op.drop_table('document')
    with op.batch_alter_table('machine', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_machine_install_date'))

    op.drop_table('machine')
    # ### end Alembic commands ###
