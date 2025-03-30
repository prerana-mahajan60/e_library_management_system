from flask import Blueprint, render_template, redirect, url_for, flash, session, request
import psycopg2
from flask import current_app
from config import get_db_connection

# admin-blueprint
admin_bp = Blueprint("admin", __name__, template_folder="templates")


# Admin Home Route
@admin_bp.route("/admin_home")
def admin_home():
    current_app.logger.debug("Session in admin_home: " + str(dict(session)))

    if "admin_id" not in session:
        flash("Please log in first!", "danger")
        return redirect(url_for("auth.admin_login"))

    # Fetch books from the database
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT book_id, book_name, author, year, available_copies, language, cover_image
        FROM books
        """
    )
    books = cursor.fetchall()

    print("Fetched books:")
    for book in books:
        print(book)

    cursor.close()
    connection.close()

    admin = {
        "id": session.get("admin_id"),
        "name": session.get("admin_name"),
    }

    return render_template("admin_home.html", admin=admin, books=books, admin_id=admin["id"])


# Admin Profile
@admin_bp.route("/admin/profile")
def admin_profile():
    session.pop("_flashes", None)
    if "admin_id" not in session:
        flash("Please log in first!", "danger")
        return redirect(url_for("auth.admin_login"))

    admin_id = session["admin_id"]
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT admin_id, admin_name, email, gender, total_books_added, total_books_removed, created_at
            FROM admin
            WHERE admin_id = %s
            """,
            (admin_id,),
        )
        admin = cursor.fetchone()

        if not admin:
            flash("Admin not found!", "danger")
            return redirect(url_for("admin.admin_home"))

        gender = admin[3].strip().lower() if admin[3] else "other"
        gender_image_map = {
            "male": "image/madmin.avif",
            "female": "image/fadmin2.avif",
            "other": "image/other.avif",
        }
        admin_dict = {
            "admin_id": admin[0],
            "admin_name": admin[1],
            "email": admin[2],
            "gender": admin[3],
            "total_books_added": admin[4],
            "total_books_removed": admin[5],
            "created_at": admin[6],
            "profile_image": url_for(
                "static", filename=gender_image_map.get(gender, "image/other.avif")
            ),
        }

        connection.commit()

        return render_template("admin_profile.html", admin=admin_dict)

    except Exception as e:
        flash(f"Error fetching admin data: {str(e)}", "danger")
        return redirect(url_for("admin.admin_home"))

    finally:
        cursor.close()
        connection.close()


# admin_update_profile
@admin_bp.route("/admin/update_profile", methods=["GET", "POST"])
def update_profile():
    if "admin_id" not in session:
        return redirect(url_for("auth.admin_login"))

    admin_id = session["admin_id"]
    connection = get_db_connection()
    cursor = connection.cursor()

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        gender = request.form["gender"]

        try:
            cursor.execute(
                """
                UPDATE admin
                SET admin_name = %s, email = %s, gender = %s
                WHERE admin_id = %s
                """,
                (name, email, gender, admin_id),
            )
            connection.commit()

            session["admin_name"] = name if name else session.get("admin_name")
            flash("Profile updated successfully!", "success")

        except Exception as e:
            connection.rollback()
            flash(f"⚠️ Error updating profile: {str(e)}", "danger")

        finally:
            cursor.close()
            connection.close()

        return redirect(url_for("admin.admin_profile"))

    # Fetching admin details
    cursor.execute(
        """
        SELECT admin_id, admin_name, email, gender
        FROM admin
        WHERE admin_id = %s
        """,
        (admin_id,),
    )
    admin = cursor.fetchone()

    cursor.close()
    connection.close()

    if not admin:
        flash("⚠️ Admin not found!", "warning")
        return redirect(url_for("auth.admin_login"))

    # Assign profile image based on gender
    gender = admin[3].strip().lower() if admin[3] else "other"
    gender_image_map = {
        "male": "image/madmin.avif",
        "female": "image/fadmin2.avif",
        "other": "image/other.avif",
    }
    profile_image = url_for("static", filename=gender_image_map.get(gender, "image/other.avif"))

    admin_dict = {
        "admin_id": admin[0],
        "admin_name": admin[1],
        "email": admin[2],
        "gender": admin[3],
        "profile_image": profile_image,
    }

    return render_template("update_admin_profile.html", admin=admin_dict, profile_image=profile_image)


# admin_delete_profile
@admin_bp.route("/admin/delete_profile", methods=["POST"])
def delete_profile():
    if "admin_id" not in session:
        flash("Please log in first!", "danger")
        return redirect(url_for("auth.admin_login"))

    admin_id = session["admin_id"]
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM admin WHERE admin_id = %s", (admin_id,))
        connection.commit()

        session.clear()
        flash("Your profile has been deleted successfully!", "success")

    except Exception as e:
        connection.rollback()
        flash(f"⚠️ Error deleting profile: {str(e)}", "danger")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("auth.admin_login"))


# admin_logout
@admin_bp.route("/admin_logout")
def admin_logout():
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect(url_for("auth.admin_login"))
