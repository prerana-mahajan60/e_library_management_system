from flask import Flask, render_template, redirect, url_for, send_from_directory
from flask_migrate import Migrate
from flask_compress import Compress
from routes.auth import auth_bp
from routes.books import books_bp
from routes.transactions import transactions_bp
from routes.admin import admin_bp
from routes.student import student_bp
from routes.browse_books import browse_books_bp
from config import Config
from extensions import db, bcrypt, login_manager
import os
from dotenv import load_dotenv

# Load .env Variables Early
load_dotenv()

# --------------------------- Initialize Flask App ---------------------------
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config.from_object(Config)

# --------------------------- Flask Extensions Init ---------------------------
db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)
migrate = Migrate(app, db)
Compress(app)

# --------------------------- Register Blueprints ---------------------------
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(student_bp, url_prefix="/student")
app.register_blueprint(books_bp, url_prefix="/books")
app.register_blueprint(transactions_bp, url_prefix="/transactions")
app.register_blueprint(browse_books_bp, url_prefix="/browse_books")

# --------------------------- Main Routes ---------------------------
@app.route("/")
def index():
    return render_template("login_system.html")

@app.route("/auth/login")
def admin_login_redirect():
    return redirect(url_for("auth.admin_login"))

@app.route("/auth/register")
def admin_register_redirect():
    return redirect(url_for("auth.admin_register"))

@app.route("/auth/student_login")
def student_login_redirect():
    return redirect(url_for("auth.student_login"))

@app.route("/auth/student_register")
def student_register_redirect():
    return redirect(url_for("auth.student_register"))

@app.route("/admin/admin_home")
def admin_home_redirect():
    return redirect(url_for("admin.admin_home"))

@app.route("/student/student_home")
def student_home_redirect():
    return redirect(url_for("student.student_home"))

@app.route("/books")
def books_redirect():
    return redirect(url_for("books_bp.books"))

@app.route("/transactions")
def transactions_redirect():
    return redirect(url_for("transactions_bp.transactions"))

@app.route("/browse_books")
def browse_books_redirect():
    return redirect(url_for("browse_books_bp.browse_books"))

# --------------------------- Static Files (Cached) ---------------------------
@app.route('/static/<path:filename>')
def custom_static(filename):
    return send_from_directory('static', filename, cache_timeout=31536000)

# --------------------------- App Runner ---------------------------
if __name__ == "__main__":
    with app.app_context():
        print("✅ Running Flask App on Render...")

        try:
            db.create_all()
        except Exception as e:
            print("❌ Error creating tables:", e)

        app.run(
            host="0.0.0.0",
            port=int(os.getenv("PORT", 5000)),
            debug=Config.DEBUG
        )
