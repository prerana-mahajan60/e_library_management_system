from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, Transaction, Student, Book, ReturnedBook
from sqlalchemy.orm import joinedload
import psycopg2.extras
from datetime import datetime
from main import db


transactions_bp = Blueprint("transactions_bp", __name__, template_folder="templates")


# Transactions Page (Admin Handle The Students Transactions)
@transactions_bp.route("/transactions")
def transactions_page():
    if session.get("role") != "Admin":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("auth_bp.student_login"))

    try:
        transactions = db.session.query(Transaction) \
            .join(Student, Student.student_id == Transaction.student_id) \
            .join(Book, Book.book_id == Transaction.book_id) \
            .order_by(Transaction.transaction_date.desc()) \
            .all()

        admin_name = session.get("admin_name", "Admin")
    except Exception as err:
        flash(f"Database error: {err}", "danger")
        transactions = []

    return render_template("transactions.html", transactions=transactions, admin={"name": admin_name})


# Update Transactions by Admin
@transactions_bp.route("/transactions/update/<int:transaction_id>", methods=["GET"])
def update_transaction_page(transaction_id):
    if session.get("role") != "Admin":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("transactions_bp.transactions_page"))

    try:
        transaction = db.session.query(Transaction) \
            .join(Student, Student.student_id == Transaction.student_id) \
            .join(Book, Book.book_id == Transaction.book_id) \
            .filter(Transaction.transaction_id == transaction_id) \
            .first()
    except Exception as err:
        flash(f"Error fetching transaction: {err}", "danger")
        transaction = None

    if not transaction:
        flash("Transaction not found!", "danger")
        return redirect(url_for("transactions_bp.transactions_page"))

    return render_template("update_transactions.html", transaction=transaction)


# Update Transactions (Auto-Set Return Date for Return Action)
@transactions_bp.route("/transactions/update/<int:transaction_id>", methods=["POST"])
def update_transaction(transaction_id):
    if session.get("role") != "Admin":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("transactions_bp.transactions_page"))

    action = request.form.get("action")

    try:
        transaction = Transaction.query.get(transaction_id)

        if action == "borrow":
            transaction.action = action
            transaction.due_date = datetime.now() + timedelta(days=14)
            transaction.transaction_date = datetime.now()
        elif action == "return":
            transaction.action = action
            transaction.transaction_date = datetime.now()
            transaction.due_date = None

            # Check if return record already exists
            returned_record = ReturnedBook.query.filter_by(student_id=transaction.student_id,
                                                           book_id=transaction.book_id).first()
            if not returned_record:
                new_returned_book = ReturnedBook(student_id=transaction.student_id, book_id=transaction.book_id,
                                                 return_date=datetime.now())
                db.session.add(new_returned_book)

        db.session.commit()
        flash("Transaction updated successfully!", "success")
    except Exception as err:
        db.session.rollback()
        flash(f"Error updating transaction: {err}", "danger")

    return redirect(url_for("transactions_bp.transactions_page"))


# Delete Transactions by Admin
@transactions_bp.route("/transactions/delete/<int:transaction_id>", methods=["POST"])
def delete_transaction(transaction_id):
    if session.get("role") != "Admin":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("transactions_bp.transactions_page"))

    try:
        transaction = Transaction.query.get(transaction_id)
        if not transaction:
            flash("Transaction not found!", "danger")
            return redirect(url_for("transactions_bp.transactions_page"))

        db.session.delete(transaction)
        db.session.commit()

        flash("Transaction deleted successfully!", "success")
    except Exception as err:
        db.session.rollback()
        flash(f"Error deleting transaction: {err}", "danger")

    return redirect(url_for("transactions_bp.transactions_page"))


# ------------------------------------------------For_students-------------------------------------------------

# For student_transactions....(students transactions which is on student system of logged-student)
@transactions_bp.route("/my_transactions")
def my_transactions():
    student_id = session.get("student_id")
    if not student_id:
        flash("You must be logged in to view transactions.", "danger")
        return redirect(url_for("auth_bp.student_login"))

    try:
        transactions = db.session.query(Transaction) \
            .join(Book, Book.book_id == Transaction.book_id) \
            .filter(Transaction.student_id == student_id) \
            .order_by(Transaction.transaction_date.desc()) \
            .all()

        student = Student.query.get(student_id)
        student_name = student.name if student else "Student"
    except Exception as e:
        flash(f"Error fetching transactions: {str(e)}", "danger")
        transactions = []
        student_name = "Student"

    return render_template("my_transactions.html", transactions=transactions, student_name=student_name)
