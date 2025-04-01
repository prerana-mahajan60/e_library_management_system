from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# SQLAlchemy DB instance
db = SQLAlchemy()


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


class Admin(db.Model):
    __tablename__ = 'admin'

    admin_id = db.Column(db.Integer, primary_key=True)
    admin_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    total_books_added = db.Column(db.Integer, default=0)
    total_books_removed = db.Column(db.Integer, default=0)
    gender = db.Column(db.String(20), default='other', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Admin {self.admin_name}>'


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
    role = db.Column(db.String(20), default='Student')

    def __repr__(self):
        return f'<Student {self.name}>'


class Book(db.Model):
    __tablename__ = 'books'

    book_id = db.Column(db.Integer, primary_key=True)
    book_name = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    available_copies = db.Column(db.Integer, nullable=False)
    language = db.Column(db.String(20), nullable=False)
    cover_image = db.Column(db.String(255), default='default.jpg')

    def __repr__(self):
        return f'<Book {self.book_name}>'


class BorrowedBook(db.Model):
    __tablename__ = 'borrowed_books'

    borrow_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'), nullable=False)
    borrow_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=True)

    student = db.relationship('Student', backref='borrowed_books')
    book = db.relationship('Book', backref='borrowed_books')

    def __repr__(self):
        return f'<BorrowedBook {self.book_id} by {self.student_id}>'


class ReturnedBook(db.Model):
    __tablename__ = 'returned_books'

    return_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'), nullable=False)
    return_date = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('Student', backref='returned_books')
    book = db.relationship('Book', backref='returned_books')

    def __repr__(self):
        return f'<ReturnedBook {self.book_id} by {self.student_id}>'


class Transaction(db.Model):
    __tablename__ = 'transactions'

    transaction_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'), nullable=False)
    borrow_date = db.Column(db.DateTime, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    return_date = db.Column(db.DateTime, nullable=True)
    action = db.Column(db.String(10), nullable=False)
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('Student', backref='transactions')
    book = db.relationship('Book', backref='transactions')

    def __repr__(self):
        return f'<Transaction {self.transaction_id}>'
