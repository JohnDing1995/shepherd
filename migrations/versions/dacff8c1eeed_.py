"""empty message

Revision ID: dacff8c1eeed
Revises: 
Create Date: 2019-06-15 16:49:17.885013

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dacff8c1eeed'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('course_repository',
    sa.Column('key', sa.String(length=50), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('key', name=op.f('pk_course_repository')),
    sa.UniqueConstraint('key', name=op.f('uq_course_repository_key'))
    )
    op.create_table('group',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('self_admin', sa.Boolean(), nullable=True),
    sa.Column('lft', sa.Integer(), nullable=False),
    sa.Column('tree_id', sa.Integer(), nullable=True),
    sa.Column('rgt', sa.Integer(), nullable=False),
    sa.Column('level', sa.Integer(), nullable=False),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['parent_id'], ['group.id'], name=op.f('fk_group_parent_id_group'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_group'))
    )
    with op.batch_alter_table('group', schema=None) as batch_op:
        batch_op.create_index('group_level_idx', ['level'], unique=False)
        batch_op.create_index('group_lft_idx', ['lft'], unique=False)
        batch_op.create_index('group_rgt_idx', ['rgt'], unique=False)
        batch_op.create_index(batch_op.f('ix_group_name'), ['name'], unique=False)

    op.create_table('group_permission',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('type', sa.Enum('subgroups', 'courses', name='permtype'), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_group_permission'))
    )
    op.create_table('user',
    sa.Column('id', sa.String(length=120), nullable=False),
    sa.Column('email', sa.String(length=50), nullable=False),
    sa.Column('display_name', sa.String(length=50), nullable=True),
    sa.Column('sorting_name', sa.String(length=50), nullable=True),
    sa.Column('full_name', sa.String(length=100), nullable=True),
    sa.Column('roles', sa.String(length=30), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_user')),
    sa.UniqueConstraint('email', name=op.f('uq_user_email')),
    sa.UniqueConstraint('id', name=op.f('uq_user_id'))
    )
    op.create_table('course_instance',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('key', sa.String(length=50), nullable=False),
    sa.Column('course_key', sa.String(length=50), nullable=False),
    sa.Column('git_origin', sa.String(length=255), nullable=True),
    sa.Column('secret_token', sa.String(length=127), nullable=True),
    sa.Column('config_filename', sa.String(length=127), nullable=True),
    sa.Column('branch', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['course_key'], ['course_repository.key'], name=op.f('fk_course_instance_course_key_course_repository')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_course_instance'))
    )
    op.create_table('create_course_perm',
    sa.Column('group_id', sa.Integer(), nullable=False),
    sa.Column('regexp', sa.Boolean(), nullable=True),
    sa.Column('pattern', sa.String(length=30), nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['group.id'], name=op.f('fk_create_course_perm_group_id_group')),
    sa.PrimaryKeyConstraint('group_id', name=op.f('pk_create_course_perm'))
    )
    op.create_table('create_group_perm',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('group_id', sa.Integer(), nullable=False),
    sa.Column('target_group_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['group_id', 'target_group_id'], ['group.id', 'group.id'], name=op.f('fk_create_group_perm_group_id_group')),
    sa.ForeignKeyConstraint(['group_id'], ['group.id'], name=op.f('fk_create_group_perm_group_id_group')),
    sa.ForeignKeyConstraint(['target_group_id'], ['group.id'], name=op.f('fk_create_group_perm_target_group_id_group')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_create_group_perm'))
    )
    op.create_table('gc_table',
    sa.Column('group_id', sa.Integer(), nullable=True),
    sa.Column('course_key', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['course_key'], ['course_repository.key'], name=op.f('fk_gc_table_course_key_course_repository')),
    sa.ForeignKeyConstraint(['group_id'], ['group.id'], name=op.f('fk_gc_table_group_id_group'))
    )
    op.create_table('gm_table',
    sa.Column('group_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['group.id'], name=op.f('fk_gm_table_group_id_group')),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name=op.f('fk_gm_table_user_id_user'))
    )
    op.create_table('gp_table',
    sa.Column('group_id', sa.Integer(), nullable=True),
    sa.Column('permission_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['group.id'], name=op.f('fk_gp_table_group_id_group')),
    sa.ForeignKeyConstraint(['permission_id'], ['group_permission.id'], name=op.f('fk_gp_table_permission_id_group_permission'))
    )
    op.create_table('build',
    sa.Column('instance_id', sa.Integer(), nullable=False),
    sa.Column('number', sa.Integer(), nullable=False),
    sa.Column('start_time', sa.DateTime(), nullable=True),
    sa.Column('end_time', sa.DateTime(), nullable=True),
    sa.Column('state', sa.Enum('PUBLISH', 'RUNNING', 'FINISHED', 'FAILED', name='state'), nullable=True),
    sa.Column('action', sa.Enum('CLONE', 'BUILD', 'DEPLOY', 'CLEAN', name='action'), nullable=True),
    sa.ForeignKeyConstraint(['instance_id'], ['course_instance.key'], name=op.f('fk_build_instance_id_course_instance')),
    sa.PrimaryKeyConstraint('instance_id', 'number', name=op.f('pk_build'))
    )
    op.create_table('build_log',
    sa.Column('instance_id', sa.Integer(), nullable=False),
    sa.Column('number', sa.Integer(), nullable=False),
    sa.Column('action', sa.Enum('CLONE', 'BUILD', 'DEPLOY', 'CLEAN', name='action'), nullable=False),
    sa.Column('start_time', sa.DateTime(), nullable=True),
    sa.Column('end_time', sa.DateTime(), nullable=True),
    sa.Column('log_text', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['instance_id'], ['build.instance_id'], name=op.f('fk_build_log_instance_id_build')),
    sa.ForeignKeyConstraint(['number'], ['build.number'], name=op.f('fk_build_log_number_build')),
    sa.PrimaryKeyConstraint('instance_id', 'number', 'action', name=op.f('pk_build_log'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('build_log')
    op.drop_table('build')
    op.drop_table('gp_table')
    op.drop_table('gm_table')
    op.drop_table('gc_table')
    op.drop_table('create_group_perm')
    op.drop_table('create_course_perm')
    op.drop_table('course_instance')
    op.drop_table('user')
    op.drop_table('group_permission')
    with op.batch_alter_table('group', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_group_name'))
        batch_op.drop_index('group_rgt_idx')
        batch_op.drop_index('group_lft_idx')
        batch_op.drop_index('group_level_idx')

    op.drop_table('group')
    op.drop_table('course_repository')
    # ### end Alembic commands ###
