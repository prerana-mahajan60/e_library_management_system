from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from models import Admin, Student  # Import models for Admin and Student

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

        # Check if email already exists
        admin = Admin.query.filter_by(email=email).first()
        if admin:
            flash("Error: Email already exists!", "danger")
            return redirect(url_for("auth.admin_register"))

        try:
            # Insert new admin data
            new_admin = Admin(admin_name=name, email=email, password=hashed_password, gender=gender)
            db.session.add(new_admin)
            db.session.commit()

            flash("Admin Registered Successfully! Please log in.", "success")
            return redirect(url_for("auth.admin_login"))

        except Exception as e:
            db.session.rollback()
            flash(f"Database Error: {str(e)}", "danger")

        return redirect(url_for("auth.admin_register"))

    return render_template("admin_register.html")


# Admin_Login
@auth_bp.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"].strip()

        # Get Admin from Database
        admin = Admin.query.filter_by(email=email).first()

        if admin:
            db_password = admin.password  # Get stored password

            # Checking password validity
            if bcrypt.check_password_hash(db_password, password):
                session.clear()
                session["admin_id"] = admin.admin_id
                session["admin_name"] = admin.admin_name
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

        # Check if email already exists
        student = Student.query.filter_by(email=email).first()
        if student:
            flash("Email already exists!", "danger")
            return redirect(url_for("auth.student_register"))

        try:
            # Insert new student data
            new_student = Student(email=email, password=hashed_password, course=course, gender=gender, name=name)
            db.session.add(new_student)
            db.session.commit()

            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("auth.student_login"))

        except Exception as e:
            db.session.rollback()
            flash(f"Registration failed: {str(e)}", "danger")

        return redirect(url_for("auth.student_register"))

    return render_template("student_register.html")


# Student_Login
@auth_bp.route("/student_login", methods=["GET", "POST"])
def student_login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        # Get Student from Database
        student = Student.query.filter_by(email=email).first()

        if student:
            db_password = student.password  # Get stored password

            # Check password
            if bcrypt.check_password_hash(db_password, password):
                session.clear()
                session["student_id"] = student.student_id
                session["username"] = student.name
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
