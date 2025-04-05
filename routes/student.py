from flask import Blueprint, render_template, redirect, url_for, flash, session, current_app, request
from models import Book, Student  # Assuming these models are defined in models.py
import traceback
from extensions import db, bcrypt, login_manager

student_bp = Blueprint("student", __name__, template_folder="templates")

# Students Home
@student_bp.route("/student_home", endpoint="student_home")
def student_home():
    print("👀 Session Data: ", session)  # Debug
    if "student_id" not in session or session.get("role") != "Student":
        flash("Please log in first!", "danger")
        return redirect(url_for("auth.student_login"))

    try:
        # Fetching available books
        books = Book.query.all()

        # Sorting books by language
        books_by_language = {
            "English": [],
            "Hindi": [],
            "Marathi": [],
        }
        for book in books:
            lang = book.language if book.language else "English"
            if lang in books_by_language:
                books_by_language[lang].append(book)
            else:
                books_by_language["English"].append(book)

    except Exception as e:
        current_app.logger.error(f"Error fetching books: {str(e)}")
        flash("Error fetching data.", "danger")
        books_by_language = {}

    student_info = {
        "name": session.get("username"),
        "student_id": session.get("student_id"),
    }

    return render_template("student_home.html", student=student_info, books_by_language=books_by_language)


# Student Profile
@student_bp.route("/student_profile")
def student_profile():
    session.pop("_flashes", None)
    if "student_id" not in session:
        flash("Please log in first!", "danger")
        return redirect(url_for("auth.student_login"))

    session.modified = True  # Ensure session is modified and refreshed

    student_id = session["student_id"]

    try:
        # Fetching student data using SQLAlchemy
        student_data = Student.query.filter_by(student_id=student_id).first()

        if not student_data:
            flash("⚠️ No student data found.", "warning")
            return redirect(url_for("auth.student_home"))

        # Profile image select based on gender
        gender = student_data.gender.strip().lower() if student_data.gender else "other"
        gender_image_map = {
            "male": "static/image/mstud4.avif",
            "female": "static/image/fstud4.avif",
            "other": "static/image/other.avif",
        }
        student_dict = {
            "student_id": student_data.student_id,
            "name": student_data.name,
            "email": student_data.email,
            "course": student_data.course,
            "gender": student_data.gender,
            "role": student_data.role,
            "total_books_borrowed": student_data.total_books_borrowed,
            "total_books_returned": student_data.total_books_returned,
            "profile_image": gender_image_map.get(gender, "static/image/other.avif"),
        }

    except Exception as e:
        current_app.logger.error(f"Error fetching student data: {str(e)}")
        flash("Error fetching profile data.", "danger")
        return redirect(url_for("auth.student_login"))

    return render_template("student_profile.html", student=student_dict)


# Update Student Profile
@student_bp.route("/update_profile", methods=["GET", "POST"])
def update_profile():
    if "student_id" not in session:
        flash("Unauthorized Access!", "danger")
        return redirect(url_for("auth.student_login"))

    student_id = session["student_id"]

    if request.method == "POST":
        # Capturing form data
        new_name = request.form.get("name", "").strip()
        new_email = request.form.get("email", "").strip()
        new_course = request.form.get("course", "").strip()
        new_gender = request.form.get("gender", "").strip().lower()

        if not new_name or not new_email or not new_course or not new_gender:
            flash("Please fill in all fields.", "danger")
            return redirect(url_for("student.update_profile"))

        try:
            # Update `student` using SQLAlchemy
            student = Student.query.filter_by(student_id=student_id).first()
            student.name = new_name
            student.email = new_email
            student.course = new_course
            student.gender = new_gender
            db.session.commit()

            # Updating session data
            session["username"] = new_name
            session["email"] = new_email
            session["gender"] = new_gender

            flash("Profile updated successfully!", "success")
            return redirect(url_for("student.student_profile"))

        except Exception:
            db.session.rollback()
            current_app.logger.error(f"Error updating profile: {traceback.format_exc()}")
            flash("Could not update profile.", "danger")

    else:
        try:
            student = Student.query.filter_by(student_id=student_id).first()

            if student:
                student_dict = {
                    "name": student.name,
                    "email": student.email,
                    "course": student.course,
                    "gender": student.gender,
                }
            else:
                student_dict = {}

        except Exception as e:
            current_app.logger.error(f"Error fetching profile data: {str(e)}")
            flash("Could not fetch profile data.", "danger")
            student_dict = {}

        # Determining profile image based on gender
        gender = student_dict.get("gender", "").strip().lower()
        gender_image_map = {
            "male": "static/image/mstud4.avif",
            "female": "static/image/fstud4.avif",
            "other": "static/image/other.avif",
        }
        profile_image = gender_image_map.get(gender, "static/image/other.avif")

        return render_template("update_profile.html", student=student_dict, profile_image=profile_image)


# Delete Student Profile
@student_bp.route("/delete_profile", methods=["POST"])
def delete_profile():
    if "student_id" not in session:
        flash("Unauthorized Access!", "danger")
        return redirect(url_for("auth.student_login"))

    student_id = session["student_id"]

    try:
        student = Student.query.filter_by(student_id=student_id).first()
        db.session.delete(student)
        db.session.commit()

        session.clear()
        flash("Profile deleted successfully!", "info")
        return redirect(url_for("auth.student_login"))

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting profile: {str(e)}")
        flash("Could not delete profile!", "danger")

    return redirect(url_for("student.student_profile"))


# Getting students list page on admin system
@student_bp.route("/students_list")
def students_list_page():
    try:
        students = Student.query.all()

        students_list = [
            {
                "student_id": student.student_id,
                "name": student.name,
                "email": student.email,
                "course": student.course,
                "gender": student.gender,
            }
            for student in students
        ]

    except Exception as e:
        current_app.logger.error(f"Error fetching student list: {str(e)}")
        students_list = []

    return render_template("students_list.html", students=students_list)


# Remove Student Profile
@student_bp.route("/remove_student/<int:student_id>", methods=["POST"])
def remove_student(student_id):
    try:
        student = Student.query.filter_by(student_id=student_id).first()
        db.session.delete(student)
        db.session.commit()
        flash("Student removed successfully!", "info")

    except Exception as e:
        db.session.rollback()
        flash(f"Error removing student: {str(e)}", "danger")

    return redirect(url_for("student.students_list_page"))


# Student Logout
@student_bp.route("/student_logout")
def student_logout():
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect(url_for("auth.student_login"))
