"""initial migration

Revision ID: 51f2198e9ca9
Revises: 
Create Date: 2025-11-25 15:02:35.112939

"""
import sqlalchemy as sa

from alembic import op

revision = '51f2198e9ca9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('users',
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('display_name', sa.String(length=255), nullable=False),
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_table('items',
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('kind', sa.Enum('book', 'article', name='item_kind'), nullable=False),
    sa.Column('status', sa.Enum('planned', 'reading', 'done', name='item_status'), nullable=False),
    sa.Column('priority', sa.Enum('low', 'normal', 'high', name='item_priority'), server_default='normal', nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tags',
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'name', name='uq_tags_user_id_name')
    )
    op.create_table('item_tags',
    sa.Column('item_id', sa.BigInteger(), nullable=False),
    sa.Column('tag_id', sa.BigInteger(), nullable=False),
    sa.ForeignKeyConstraint(['item_id'], ['items.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('item_id', 'tag_id'),
    )

def downgrade():
    op.drop_table('item_tags')
    op.drop_table('tags')
    op.drop_table('items')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')