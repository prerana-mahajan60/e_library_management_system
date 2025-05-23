"""Fixed DB instance

Revision ID: 65bbb1b9eb87
Revises: 
Create Date: 2025-04-02 12:10:17.099193

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '65bbb1b9eb87'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('admin',
    sa.Column('admin_id', sa.Integer(), nullable=False),
    sa.Column('admin_name', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.Column('total_books_added', sa.Integer(), nullable=True),
    sa.Column('total_books_removed', sa.Integer(), nullable=True),
    sa.Column('gender', sa.String(length=20), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('admin_id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('books',
    sa.Column('book_id', sa.Integer(), nullable=False),
    sa.Column('book_name', sa.String(length=255), nullable=False),
    sa.Column('author', sa.String(length=255), nullable=False),
    sa.Column('year', sa.Integer(), nullable=False),
    sa.Column('available_copies', sa.Integer(), nullable=False),
    sa.Column('language', sa.String(length=20), nullable=False),
    sa.Column('cover_image', sa.String(length=255), nullable=True),
    sa.CheckConstraint('available_copies >= 0', name='check_available_copies_positive'),
    sa.CheckConstraint('year > 0', name='check_year_positive'),
    sa.PrimaryKeyConstraint('book_id')
    )
    op.create_table('student',
    sa.Column('student_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.Column('course', sa.String(length=100), nullable=True),
    sa.Column('gender', sa.String(length=20), nullable=False),
    sa.Column('total_books_borrowed', sa.Integer(), nullable=True),
    sa.Column('total_books_returned', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('role', sa.String(length=20), nullable=True),
    sa.PrimaryKeyConstraint('student_id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('users',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.Column('role', sa.String(length=20), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('user_id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('borrowed_books',
    sa.Column('borrow_id', sa.Integer(), nullable=False),
    sa.Column('student_id', sa.Integer(), nullable=False),
    sa.Column('book_id', sa.Integer(), nullable=False),
    sa.Column('borrow_date', sa.DateTime(), nullable=True),
    sa.Column('due_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['book_id'], ['books.book_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['student_id'], ['student.student_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('borrow_id')
    )
    op.create_table('returned_books',
    sa.Column('return_id', sa.Integer(), nullable=False),
    sa.Column('student_id', sa.Integer(), nullable=False),
    sa.Column('book_id', sa.Integer(), nullable=False),
    sa.Column('return_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['book_id'], ['books.book_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['student_id'], ['student.student_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('return_id')
    )
    op.create_table('transactions',
    sa.Column('transaction_id', sa.Integer(), nullable=False),
    sa.Column('student_id', sa.Integer(), nullable=False),
    sa.Column('book_id', sa.Integer(), nullable=False),
    sa.Column('borrow_date', sa.DateTime(), nullable=True),
    sa.Column('due_date', sa.DateTime(), nullable=True),
    sa.Column('return_date', sa.DateTime(), nullable=True),
    sa.Column('action', sa.Enum('borrow', 'return', name='transaction_action'), nullable=False),
    sa.Column('transaction_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['book_id'], ['books.book_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['student_id'], ['student.student_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('transaction_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('transactions')
    op.drop_table('returned_books')
    op.drop_table('borrowed_books')
    op.drop_table('users')
    op.drop_table('student')
    op.drop_table('books')
    op.drop_table('admin')
    # ### end Alembic commands ###
