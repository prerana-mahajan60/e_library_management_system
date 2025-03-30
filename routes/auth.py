from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from config import get_db_connection
from werkzeug.security import check_password_hash, generate_password_hash
import psycopg2
from psycopg2 import sql
from flask_bcrypt import Bcrypt

auth_bp = Blueprint("auth", __name__, template_folder="templates")

# Initialize Bcrypt
bcrypt = Bcrypt()


# ---------------------------------------------Admin-------------------------------------------------------
# Admin_Register
@auth_bp.route("/admin_register", methods=["GET", "POST"])
def admin_register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        password = request.form["password"].strip()
        gender = request.form["gender"].strip().lower()

        # Validate Required Fields
        if not name or not email or not password or not gender:
            flash("All fields are required!", "danger")
            return redirect(url_for("auth.admin_register"))

        # Hash password for security
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        # Get database connection
        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            # Check if email already exists
            cursor.execute("SELECT email FROM admin WHERE email = %s", (email,))
            if cursor.fetchone():
                flash("Error: Email already exists!", "danger")
                return redirect(url_for("auth.admin_register"))

            # Insert new admin data
            cursor.execute(
                """
                INSERT INTO admin (admin_name, email, password, gender)
                VALUES (%s, %s, %s, %s)
                """,
                (name, email, hashed_password, gender),
            )
            connection.commit()

            flash("Admin Registered Successfully! Please log in.", "success")
            return redirect(url_for("auth.admin_login"))

        except psycopg2.Error as e:
            connection.rollback()
            flash(f"Database Error: {str(e)}", "danger")

        finally:
            cursor.close()
            connection.close()

    return render_template("admin_register.html")


# Admin_Login
@auth_bp.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"].strip()

        # Get database connection
        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("SELECT * FROM admin WHERE email = %s", (email,))
            admin = cursor.fetchone()

        except psycopg2.Error:
            flash("Database error occurred! Please try again.", "danger")
            admin = None

        finally:
            cursor.close()
            connection.close()

        if admin:
            db_password = admin[3]  # 3rd column is password

            # Checking password validity
            if db_password and bcrypt.check_password_hash(db_password, password):
                session.clear()
                session["admin_id"] = admin[0]
                session["admin_name"] = admin[1]
                session["role"] = "Admin"

                flash("Login Successful!", "success")
                return redirect(url_for("admin.admin_home"))

            else:
                flash("Incorrect password!", "danger")

        else:
            flash("Invalid Email or Password!", "danger")

    return render_template("admin_login.html")


# ------------------------------------Student--------------------------------------------------
# Student_Register
@auth_bp.route("/student_register", methods=["GET", "POST"])
def student_register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        course = request.form.get("course", "").strip()
        gender = request.form.get("gender", "").strip()

        # Validate Required Fields
        if not name or not email or not password or not course or not gender:
            flash("All fields are required!", "danger")
            return redirect(url_for("auth.student_register"))

        # Hash password
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        # Get database connection
        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            # Check if email already exists
            cursor.execute("SELECT email FROM student WHERE email = %s", (email,))
            if cursor.fetchone():
                flash("Email already exists!", "danger")
                return redirect(url_for("auth.student_register"))

            # Insert new student data
            cursor.execute(
                """
                INSERT INTO student (email, password, course, gender, name) 
                VALUES (%s, %s, %s, %s, %s)
                """,
                (email, hashed_password, course, gender, name),
            )
            connection.commit()

            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("auth.student_login"))

        except psycopg2.Error as e:
            connection.rollback()
            flash(f"Registration failed: {str(e)}", "danger")

        finally:
            cursor.close()
            connection.close()

    return render_template("student_register.html")


# Student_Login
@auth_bp.route("/student_login", methods=["GET", "POST"])
def student_login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        # Get database connection
        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("SELECT * FROM student WHERE email = %s", (email,))
            student = cursor.fetchone()

        except psycopg2.Error:
            flash("Database error occurred! Please try again.", "danger")
            student = None

        finally:
            cursor.close()
            connection.close()

        if student:
            db_password = student[3]  # 3rd column is password

            # Check password
            if db_password and bcrypt.check_password_hash(db_password, password):
                session.clear()
                session["student_id"] = student[0]
                session["username"] = student[1]
                session["role"] = "Student"

                flash("Login Successful!", "success")
                return redirect(url_for("student.student_home"))

            else:
                flash("Incorrect password!", "danger")

        else:
            flash("Invalid Email or Password!", "danger")

    return render_template("student_login.html")


# Logout
@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Logged Out Successfully!", "info")
    return redirect(url_for("auth.login_system"))


# Login_System
@auth_bp.route("/login_system")
def login_system():
    return render_template("login_system.html")
