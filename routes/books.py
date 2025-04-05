from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from config import db  # Import the db object for SQLAlchemy
from models import Book, Admin  # Assuming these models are defined in models.py
from main import db


# books_blueprint
books_bp = Blueprint('books_bp', __name__, template_folder="templates")


# To display books
@books_bp.route('/books', methods=['GET'])
def books():
    # Fetching books using SQLAlchemy
    books = Book.query.all()

    # Sort books by language
    books_by_language = {}
    for book in books:
        lang = book.language
        if lang not in books_by_language:
            books_by_language[lang] = []
        books_by_language[lang].append({
            "book_id": book.book_id,
            "book_name": book.book_name,
            "author": book.author,
            "year": book.year,
            "available_copies": book.available_copies,
            "language": book.language
        })

    return render_template('books.html', books_by_language=books_by_language, role="Admin")


# To add a new book (Admin only)
@books_bp.route('/books/add', methods=['POST'])
def add_book():
    book_name = request.form['book_name']
    author = request.form['author']
    year = request.form['year']
    available_copies = request.form['available_copies']
    language = request.form['language']
    admin_id = session.get("admin_id")

    # Adding new book using SQLAlchemy
    new_book = Book(
        book_name=book_name,
        author=author,
        year=year,
        available_copies=available_copies,
        language=language
    )
    db.session.add(new_book)

    # Updating total_books_added for admin
    admin = Admin.query.filter_by(admin_id=admin_id).first()
    admin.total_books_added += 1

    db.session.commit()

    flash('Book added successfully!', 'success')
    return redirect(url_for('books_bp.books'))


# Route to delete a book (Admin only)
@books_bp.route('/books/delete/<int:book_id>', methods=['GET'])
def delete_book(book_id):
    admin_id = session.get("admin_id")

    # Delete the book using SQLAlchemy
    book_to_delete = Book.query.filter_by(book_id=book_id).first()
    db.session.delete(book_to_delete)

    # Update total_books_removed for admin
    admin = Admin.query.filter_by(admin_id=admin_id).first()
    admin.total_books_removed += 1

    db.session.commit()

    flash('Book removed successfully!', 'success')
    return redirect(url_for('books_bp.books'))


# To update book details (Admin only)
@books_bp.route('/books/update/<int:book_id>', methods=['GET', 'POST'])
def update_book(book_id):
    if request.method == 'POST':
        book_name = request.form['book_name']
        author = request.form['author']
        year = request.form['year']
        available_copies = request.form['available_copies']
        language = request.form['language']

        # Update book details using SQLAlchemy
        book = Book.query.filter_by(book_id=book_id).first()
        book.book_name = book_name
        book.author = author
        book.year = year
        book.available_copies = available_copies
        book.language = language

        db.session.commit()

        flash('Book updated successfully!', 'success')
        return redirect(url_for('books_bp.books'))

    book = Book.query.filter_by(book_id=book_id).first()

    if book:
        book_data = {
            "book_id": book.book_id,
            "book_name": book.book_name,
            "author": book.author,
            "year": book.year,
            "available_copies": book.available_copies,
            "language": book.language
        }
    else:
        book_data = {}

    return render_template('update_book.html', book=book_data)
