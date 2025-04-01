from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from flask_sqlalchemy import SQLAlchemy
from flask import current_app
from models import Admin, Book  # Import the Admin and Book models

# admin-blueprint
admin_bp = Blueprint("admin", __name__, template_folder="templates")

# Admin Home Route
@admin_bp.route("/admin_home")
def admin_home():
    current_app.logger.debug("Session in admin_home: " + str(dict(session)))

    if "admin_id" not in session:
        flash("Please log in first!", "danger")
        return redirect(url_for("auth.admin_login"))

    # Fetch books from the database using SQLAlchemy
    books = Book.query.all()

    print("Fetched books:")
    for book in books:
        print(book)

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
    admin = Admin.query.get(admin_id)

    if not admin:
        flash("Admin not found!", "danger")
        return redirect(url_for("admin.admin_home"))

    gender = admin.gender.strip().lower() if admin.gender else "other"
    gender_image_map = {
        "male": "image/madmin.avif",
        "female": "image/fadmin2.avif",
        "other": "image/other.avif",
    }
    admin_dict = {
        "admin_id": admin.admin_id,
        "admin_name": admin.admin_name,
        "email": admin.email,
        "gender": admin.gender,
        "total_books_added": admin.total_books_added,
        "total_books_removed": admin.total_books_removed,
        "created_at": admin.created_at,
        "profile_image": url_for(
            "static", filename=gender_image_map.get(gender, "image/other.avif")
        ),
    }

    return render_template("admin_profile.html", admin=admin_dict)

# admin_update_profile
@admin_bp.route("/admin/update_profile", methods=["GET", "POST"])
def update_profile():
    if "admin_id" not in session:
        return redirect(url_for("auth.admin_login"))

    admin_id = session["admin_id"]
    admin = Admin.query.get(admin_id)

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        gender = request.form["gender"]

        try:
            admin.admin_name = name
            admin.email = email
            admin.gender = gender
            db.session.commit()

            session["admin_name"] = name if name else session.get("admin_name")
            flash("Profile updated successfully!", "success")

        except Exception as e:
            db.session.rollback()
            flash(f"⚠️ Error updating profile: {str(e)}", "danger")

        return redirect(url_for("admin.admin_profile"))

    # Assign profile image based on gender
    gender = admin.gender.strip().lower() if admin.gender else "other"
    gender_image_map = {
        "male": "image/madmin.avif",
        "female": "image/fadmin2.avif",
        "other": "image/other.avif",
    }
    profile_image = url_for("static", filename=gender_image_map.get(gender, "image/other.avif"))

    admin_dict = {
        "admin_id": admin.admin_id,
        "admin_name": admin.admin_name,
        "email": admin.email,
        "gender": admin.gender,
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
    admin = Admin.query.get(admin_id)

    try:
        db.session.delete(admin)
        db.session.commit()

        session.clear()
        flash("Your profile has been deleted successfully!", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"⚠️ Error deleting profile: {str(e)}", "danger")

    return redirect(url_for("auth.admin_login"))

# admin_logout
@admin_bp.route("/admin_logout")
def admin_logout():
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect(url_for("auth.admin_login"))
