from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime, timedelta
from config import db  # Import the db object for SQLAlchemy
from models import Book, BorrowedBook, Transaction, Student, ReturnedBook  # Import the necessary models

# Set IST timezone
import pytz
IST = pytz.timezone('Asia/Kolkata')

# browse_books_blueprint
browse_books_bp = Blueprint('browse_books_bp', __name__, template_folder="templates")


# To display available books
@browse_books_bp.route('/browse_books')
def browse_books():
    student_id = request.args.get('student_id')

    # Fetching books using SQLAlchemy
    available_books = Book.query.filter(Book.available_copies > 0).all()

    books_by_language = {'English': [], 'Hindi': [], 'Marathi': []}
    for book in available_books:
        lang = book.language
        if lang in books_by_language:
            books_by_language[lang].append({
                "book_id": book.book_id,
                "book_name": book.book_name,
                "author": book.author,
                "year": book.year,
                "available_copies": book.available_copies,
                "language": book.language
            })

    return render_template(
        'browse_books.html',
        books_by_language=books_by_language,
        student_id=student_id
    )


# To display borrowed books
@browse_books_bp.route('/borrowed_books')
def borrowed_books():
    student_id = session.get("student_id")
    if not student_id:
        flash("Error: Student ID not found in session!", "danger")
        return redirect(url_for("auth.student_login"))

    # Fetching borrowed books using SQLAlchemy
    borrowed_books = db.session.query(BorrowedBook, Book).filter(
        BorrowedBook.student_id == student_id,
        BorrowedBook.return_date == None
    ).join(Book, BorrowedBook.book_id == Book.book_id).all()

    books_data = []
    for borrow_record, book in borrowed_books:
        books_data.append({
            "borrow_id": borrow_record.borrow_id,
            "book_name": book.book_name,
            "author": book.author,
            "year": book.year,
            "language": book.language,
            "borrow_date": borrow_record.borrow_date,
            "due_date": borrow_record.due_date
        })

    return render_template("borrowed_books.html", borrowed_books=books_data)


# To borrow a book
@browse_books_bp.route('/borrow_book/<int:book_id>', methods=['POST'])
def borrow_book(book_id):
    student_id = session.get("student_id")
    if not student_id:
        flash("You must be logged in to borrow a book.", "danger")
        return redirect(url_for('auth.student_login'))

    # Check if the student already borrowed the book and not returned it
    already_borrowed = BorrowedBook.query.filter_by(student_id=student_id, book_id=book_id, return_date=None).count()

    if already_borrowed > 0:
        flash("You have already borrowed this book. Return it before borrowing again.", "danger")
        return redirect(url_for('browse_books_bp.borrowed_books'))

    # Get available copies
    book = Book.query.filter_by(book_id=book_id).first()

    if book and book.available_copies > 0:
        # Decrease available copies by 1
        book.available_copies -= 1

        borrow_date = datetime.now(IST)
        due_date = borrow_date + timedelta(days=14)

        # Create BorrowedBook entry
        borrowed_book = BorrowedBook(
            student_id=student_id,
            book_id=book_id,
            borrow_date=borrow_date,
            due_date=due_date
        )
        db.session.add(borrowed_book)

        # Log transaction with return_date as NULL on borrow
        transaction = Transaction(
            student_id=student_id,
            book_id=book_id,
            action='borrow',
            borrow_date=borrow_date,
            due_date=due_date,
            return_date=None,
            transaction_date=borrow_date
        )
        db.session.add(transaction)

        # Increment total_books_borrowed for student
        student = Student.query.filter_by(student_id=student_id).first()
        student.total_books_borrowed += 1

        db.session.commit()

        flash("Book borrowed successfully!", "success")
    else:
        flash("Book is not available!", "danger")

    return redirect(url_for('browse_books_bp.borrowed_books'))


# To return a book
@browse_books_bp.route('/return_book/<int:borrow_id>', methods=['POST'])
def return_book(borrow_id):
    student_id = session.get("student_id")
    if not student_id:
        flash("You must be logged in to return a book.", "danger")
        return redirect(url_for("auth.student_login"))

    try:
        borrow_record = BorrowedBook.query.filter_by(borrow_id=borrow_id, return_date=None).first()
        if not borrow_record:
            flash("Borrow record not found or already returned!", "danger")
            return redirect(url_for("browse_books_bp.borrowed_books"))

        book = Book.query.filter_by(book_id=borrow_record.book_id).first()

        return_date = datetime.now(IST)

        # Update the return_date of the borrow record
        borrow_record.return_date = return_date

        # Increase available copies after returning
        book.available_copies += 1

        # Increment total_books_returned for student
        student = Student.query.filter_by(student_id=student_id).first()
        student.total_books_returned += 1

        # Log return transaction
        transaction = Transaction(
            student_id=student_id,
            book_id=book.book_id,
            action='return',
            borrow_date=borrow_record.borrow_date,
            due_date=borrow_record.due_date,
            return_date=return_date,
            transaction_date=return_date
        )
        db.session.add(transaction)

        # Insert returned book record
        returned_book = ReturnedBook(
            student_id=student_id,
            book_id=book.book_id,
            return_date=return_date
        )
        db.session.add(returned_book)

        db.session.commit()
        flash("Book returned successfully!", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Unexpected Error: {str(e)}", "danger")

    return redirect(url_for("browse_books_bp.borrowed_books"))
