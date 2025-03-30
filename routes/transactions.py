from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import psycopg2
from config import get_db_connection
import psycopg2.extras

transactions_bp = Blueprint("transactions_bp", __name__, template_folder="templates")


# Transactions Page (Admin Handle The Students Transactions)
@transactions_bp.route("/transactions")
def transactions_page():
    if session.get("role") != "Admin":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("auth_bp.student_login"))

    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    try:
        query = """
        SELECT 
            t.transaction_id, 
            t.student_id,  
            COALESCE(s.name, 'Unknown Student') AS student_name,  
            COALESCE(b.book_name, 'Unknown Book') AS book_title,  
            t.action, 
            TO_CHAR(t.borrow_date, 'YYYY-MM-DD HH24:MI:SS') AS borrow_date,
            CASE 
                WHEN t.action = 'borrow' THEN TO_CHAR(t.due_date, 'YYYY-MM-DD HH24:MI:SS')
                ELSE 'N/A'
            END AS due_date,
            CASE 
                WHEN t.action = 'return' THEN 
                    COALESCE((
                        SELECT TO_CHAR(return_date, 'YYYY-MM-DD HH24:MI:SS')
                        FROM returned_books rb 
                        WHERE rb.student_id = t.student_id AND rb.book_id = t.book_id
                        LIMIT 1
                    ), 'N/A')
                ELSE 'N/A'
            END AS return_date,
            TO_CHAR(t.transaction_date, 'YYYY-MM-DD HH24:MI:SS') AS transaction_date
        FROM transactions t
        LEFT JOIN student s ON t.student_id = s.student_id  
        LEFT JOIN books b ON t.book_id = b.book_id
        ORDER BY t.transaction_date DESC;
        """
        cursor.execute(query)
        transactions = cursor.fetchall()

        admin_name = session.get("admin_name", "Admin")

    except psycopg2.Error as err:
        flash(f"Database error: {err}", "danger")
        transactions = []
    finally:
        cursor.close()
        connection.close()

    return render_template("transactions.html", transactions=transactions, admin={"name": admin_name})


# Update Transactions by Admin
@transactions_bp.route("/transactions/update/<int:transaction_id>", methods=["GET"])
def update_transaction_page(transaction_id):
    if session.get("role") != "Admin":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("transactions_bp.transactions_page"))

    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    try:
        cursor.execute(
            """
            SELECT 
                t.transaction_id, 
                t.student_id,  
                COALESCE(s.name, 'Unknown Student') AS student_name,  
                COALESCE(b.book_name, 'Unknown Book') AS book_title,
                t.action, 
                TO_CHAR(t.borrow_date, 'YYYY-MM-DD HH24:MI:SS') AS borrow_date,
                TO_CHAR(t.due_date, 'YYYY-MM-DD HH24:MI:SS') AS due_date,
                TO_CHAR(t.transaction_date, 'YYYY-MM-DD HH24:MI:SS') AS transaction_date
            FROM transactions t
            LEFT JOIN student s ON t.student_id = s.student_id  
            LEFT JOIN books b ON t.book_id = b.book_id
            WHERE t.transaction_id = %s
            """,
            (transaction_id,)
        )

        transaction = cursor.fetchone()
    except psycopg2.Error as err:
        flash(f"Error fetching transaction: {err}", "danger")
        transaction = None
    finally:
        cursor.close()
        connection.close()

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

    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    try:
        if action == "borrow":
            # Auto-set due_date to 14 days if action is "borrow"
            cursor.execute(
                """
                UPDATE transactions 
                SET action = %s, 
                    due_date = NOW() + INTERVAL '14 days',  
                    transaction_date = NOW()
                WHERE transaction_id = %s
                """,
                (action, transaction_id),
            )
        elif action == "return":
            # Set transaction_date to NOW() if action is "return"
            cursor.execute(
                """
                UPDATE transactions 
                SET action = %s, 
                    transaction_date = NOW(),
                    due_date = NULL
                WHERE transaction_id = %s
                """,
                (action, transaction_id),
            )

            # Check if return record already exists
            cursor.execute(
                """
                SELECT return_date FROM returned_books
                WHERE student_id = (SELECT student_id FROM transactions WHERE transaction_id = %s)
                  AND book_id = (SELECT book_id FROM transactions WHERE transaction_id = %s)
                """,
                (transaction_id, transaction_id),
            )
            existing_return = cursor.fetchone()

            # If no return record, insert it
            if not existing_return:
                cursor.execute(
                    """
                    INSERT INTO returned_books (student_id, book_id, return_date)
                    SELECT student_id, book_id, NOW()
                    FROM transactions
                    WHERE transaction_id = %s
                    """,
                    (transaction_id,),
                )

        connection.commit()
        flash("Transaction updated successfully!", "success")

    except psycopg2.Error as err:
        flash(f"Error updating transaction: {err}", "danger")
        print(f"Error updating transaction: {err}")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("transactions_bp.transactions_page"))


# Delete Transactions by Admin
@transactions_bp.route("/transactions/delete/<int:transaction_id>", methods=["POST"])
def delete_transaction(transaction_id):
    if session.get("role") != "Admin":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("transactions_bp.transactions_page"))

    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    try:
        cursor.execute("SELECT transaction_id FROM transactions WHERE transaction_id = %s", (transaction_id,))
        existing_transaction = cursor.fetchone()
        if not existing_transaction:
            flash("Transaction not found!", "danger")
            return redirect(url_for("transactions_bp.transactions_page"))

        cursor.execute("DELETE FROM transactions WHERE transaction_id = %s", (transaction_id,))
        connection.commit()

        flash("Transaction deleted successfully!", "success")
    except psycopg2.Error as err:
        flash(f"Error deleting transaction: {err}", "danger")
        print(f"Error deleting transaction: {err}")
    finally:
        cursor.close()
        connection.close()

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
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Fetching transactions for logged-in student
        cursor.execute("""
            SELECT t.transaction_id, 
                   b.book_name, 
                   t.action, 
                   TO_CHAR(t.borrow_date, 'YYYY-MM-DD HH24:MI:SS') AS borrow_date,
                   CASE 
                       WHEN t.action = 'borrow' THEN TO_CHAR(t.due_date, 'YYYY-MM-DD HH24:MI:SS')
                       ELSE 'N/A'
                   END AS due_date,
                   CASE 
                       WHEN t.action = 'return' THEN 
                           COALESCE((
                               SELECT TO_CHAR(return_date, 'YYYY-MM-DD HH24:MI:SS')
                               FROM returned_books rb 
                               WHERE rb.student_id = t.student_id AND rb.book_id = t.book_id
                               LIMIT 1
                           ), 'N/A')
                       ELSE 'N/A'
                   END AS return_date,
                   TO_CHAR(t.transaction_date, 'YYYY-MM-DD HH24:MI:SS') AS transaction_date
            FROM transactions t
            LEFT JOIN books b ON t.book_id = b.book_id
            WHERE t.student_id = %s
            ORDER BY t.transaction_date DESC
        """, (student_id,))

        transactions = cursor.fetchall()

        # Fetching student name
        cursor.execute("SELECT name FROM student WHERE student_id = %s", (student_id,))
        student = cursor.fetchone()
        student_name = student["name"] if student else "Student"

    except Exception as e:
        flash(f"Error fetching transactions: {str(e)}", "danger")
        transactions = []
        student_name = "Student"

    finally:
        cursor.close()
        connection.close()

    return render_template("my_transactions.html", transactions=transactions, student_name=student_name)

