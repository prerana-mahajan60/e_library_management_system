from flask import Blueprint, render_template, redirect, url_for, flash, session, current_app, request
from config import get_db_connection
import traceback

student_bp = Blueprint("student", __name__, template_folder="templates")

# Students Home
@student_bp.route("/student_home", endpoint="student_home")
def student_home():
    print("👀 Session Data: ", session)  # Debug
    if "student_id" not in session or session.get("role") != "Student":
        flash("Please log in first!", "danger")
        return redirect(url_for("auth.student_login"))

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Fetching available books
        cursor.execute(
            """
            SELECT book_id, book_name, author, year, available_copies, language, cover_image 
            FROM books
            """
        )
        books = cursor.fetchall()

        # Sorting books by language
        books_by_language = {
            "English": [],
            "Hindi": [],
            "Marathi": [],
        }
        for book in books:
            lang = book[5] if book[5] else "English"
            if lang in books_by_language:
                books_by_language[lang].append(
                    {
                        "book_id": book[0],
                        "book_name": book[1],
                        "author": book[2],
                        "year": book[3],
                        "available_copies": book[4],
                        "language": book[5],
                        "cover_image": book[6],
                    }
                )
            else:
                books_by_language["English"].append(book)

    except Exception as e:
        current_app.logger.error(f"Error fetching books: {str(e)}")
        flash("Error fetching data.", "danger")
        books_by_language = {}

    finally:
        cursor.close()
        connection.close()

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
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Fetching student data
        cursor.execute(
            """
            SELECT student_id, name, email, course, gender, role, total_books_borrowed, total_books_returned
            FROM student
            WHERE student_id = %s
            """,
            (student_id,),
        )
        student_data = cursor.fetchone()

        if not student_data:
            flash("⚠️ No student data found.", "warning")
            return redirect(url_for("auth.student_home"))

        # Profile image select based on gender
        gender = student_data[4].strip().lower() if student_data[4] else "other"
        gender_image_map = {
            "male": "static/image/mstud4.avif",
            "female": "static/image/fstud4.avif",
            "other": "static/image/other.avif",
        }
        student_dict = {
            "student_id": student_data[0],
            "name": student_data[1],
            "email": student_data[2],
            "course": student_data[3],
            "gender": student_data[4],
            "role": student_data[5],
            "total_books_borrowed": student_data[6],
            "total_books_returned": student_data[7],
            "profile_image": gender_image_map.get(gender, "static/image/other.avif"),
        }

    except Exception as e:
        current_app.logger.error(f"Error fetching student data: {str(e)}")
        flash("Error fetching profile data.", "danger")
        return redirect(url_for("auth.student_login"))

    finally:
        cursor.close()
        connection.close()

    return render_template("student_profile.html", student=student_dict)


# Update Student Profile
@student_bp.route("/update_profile", methods=["GET", "POST"])
def update_profile():
    if "student_id" not in session:
        flash("Unauthorized Access!", "danger")
        return redirect(url_for("auth.student_login"))

    student_id = session["student_id"]
    connection = get_db_connection()
    cursor = connection.cursor()

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
            # Update `student` table
            cursor.execute(
                """
                UPDATE student 
                SET name = %s, email = %s, course = %s, gender = %s
                WHERE student_id = %s
                """,
                (new_name, new_email, new_course, new_gender, student_id),
            )
            connection.commit()

            # Updating session data
            session["username"] = new_name
            session["email"] = new_email
            session["gender"] = new_gender

            flash("Profile updated successfully!", "success")
            return redirect(url_for("student.student_profile"))

        except Exception:
            connection.rollback()
            current_app.logger.error(f"Error updating profile: {traceback.format_exc()}")
            flash("Could not update profile.", "danger")
        finally:
            cursor.close()
            connection.close()

    else:
        try:
            cursor.execute(
                """
                SELECT name, email, course, gender
                FROM student
                WHERE student_id = %s
                """,
                (student_id,),
            )
            student = cursor.fetchone()

            if student:
                student_dict = {
                    "name": student[0],
                    "email": student[1],
                    "course": student[2],
                    "gender": student[3],
                }
            else:
                student_dict = {}

        except Exception as e:
            current_app.logger.error(f"Error fetching profile data: {str(e)}")
            flash("Could not fetch profile data.", "danger")
            student_dict = {}

        finally:
            cursor.close()
            connection.close()

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
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM student WHERE student_id = %s", (student_id,))
        connection.commit()

        session.clear()
        flash("Profile deleted successfully!", "info")
        return redirect(url_for("auth.student_login"))

    except Exception as e:
        connection.rollback()
        current_app.logger.error(f"Error deleting profile: {str(e)}")
        flash("Could not delete profile!", "danger")
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("student.student_profile"))


# Getting students list page on admin system
@student_bp.route("/students_list")
def students_list_page():
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT student_id, name, email, course, gender
            FROM student
            """
        )
        students = cursor.fetchall()

        students_list = [
            {
                "student_id": row[0],
                "name": row[1],
                "email": row[2],
                "course": row[3],
                "gender": row[4],
            }
            for row in students
        ]

    except Exception as e:
        current_app.logger.error(f"Error fetching student list: {str(e)}")
        students_list = []

    finally:
        cursor.close()
        connection.close()

    return render_template("students_list.html", students=students_list)


# Remove Student Profile
@student_bp.route("/remove_student/<int:student_id>", methods=["POST"])
def remove_student(student_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM student WHERE student_id = %s", (student_id,))
        connection.commit()
        flash("Student removed successfully!", "info")

    except Exception as e:
        connection.rollback()
        flash(f"Error removing student: {str(e)}", "danger")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("student.students_list_page"))


# Student Logout
@student_bp.route("/student_logout")
def student_logout():
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect(url_for("auth.student_login"))
