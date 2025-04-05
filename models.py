from datetime import datetime
import sqlalchemy as sa
from sqlalchemy import CheckConstraint
from extensions import db, bcrypt

# -------------------------- User Model --------------------------
class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.name}>'

# -------------------------- Admin Model --------------------------
class Admin(db.Model):
    __tablename__ = 'admin'

    admin_id = db.Column(db.Integer, primary_key=True)
    admin_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    gender = db.Column(db.String(20), default='other', nullable=False)
    total_books_added = db.Column(db.Integer, default=0)
    total_books_removed = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("gender IN ('male', 'female', 'other')", name="check_admin_gender"),
    )

    def __repr__(self):
        return f'<Admin {self.admin_name}>'

# -------------------------- Student Model --------------------------
class Student(db.Model):
    __tablename__ = 'student'

    student_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    course = db.Column(db.String(100), default='N/A')
    gender = db.Column(db.String(20), default='other', nullable=False)
    total_books_borrowed = db.Column(db.Integer, default=0)
    total_books_returned = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("gender IN ('male', 'female', 'other')", name="check_student_gender"),
    )

    def __repr__(self):
        return f'<Student {self.name}>'

# -------------------------- Book Model --------------------------
class Book(db.Model):
    __tablename__ = 'books'

    book_id = db.Column(db.Integer, primary_key=True)
    book_name = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    available_copies = db.Column(db.Integer, nullable=False)
    language = db.Column(db.String(20), nullable=False)
    cover_image = db.Column(db.String(255), default='static/images/default.jpg')

    __table_args__ = (
        CheckConstraint('year > 0', name='check_year_positive'),
        CheckConstraint('available_copies >= 0', name='check_available_copies_positive'),
    )

    def __repr__(self):
        return f'<Book {self.book_name}>'

# -------------------------- Borrowed Book Model --------------------------
class BorrowedBook(db.Model):
    __tablename__ = 'borrowed_books'

    borrow_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id', ondelete='CASCADE'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id', ondelete='CASCADE'), nullable=False)
    borrow_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime, nullable=True)  # ✅ Add this line

    student = db.relationship('Student', backref=db.backref('borrowed_books', cascade='all, delete-orphan', passive_deletes=True))
    book = db.relationship('Book', backref=db.backref('borrowed_books', cascade='all, delete-orphan', passive_deletes=True))

    def __repr__(self):
        return f'<BorrowedBook book_id={self.book_id} student_id={self.student_id}>'


# -------------------------- Returned Book Model --------------------------
class ReturnedBook(db.Model):
    __tablename__ = 'returned_books'

    return_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id', ondelete='CASCADE'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id', ondelete='CASCADE'), nullable=False)
    return_date = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('Student', backref=db.backref('returned_books', cascade='all, delete-orphan', passive_deletes=True))
    book = db.relationship('Book', backref=db.backref('returned_books', cascade='all, delete-orphan', passive_deletes=True))

    def __repr__(self):
        return f'<ReturnedBook book_id={self.book_id} student_id={self.student_id}>'

# -------------------------- Transaction Model --------------------------
class Transaction(db.Model):
    __tablename__ = 'transactions'

    transaction_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id', ondelete='CASCADE'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id', ondelete='CASCADE'), nullable=False)
    borrow_date = db.Column(db.DateTime, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    return_date = db.Column(db.DateTime, nullable=True)
    action = db.Column(sa.Enum('borrow', 'return', name='transaction_action', create_type=False), nullable=False)
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('Student', backref=db.backref('transactions', cascade='all, delete-orphan', passive_deletes=True))
    book = db.relationship('Book', backref=db.backref('transactions', cascade='all, delete-orphan', passive_deletes=True))

    def __repr__(self):
        return f'<Transaction {self.transaction_id}>'
