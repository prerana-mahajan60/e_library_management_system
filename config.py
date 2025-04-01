import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
# 🟢 Load Environment Variables from .env
load_dotenv()

db = SQLAlchemy()

class Config:
    """Configuration settings for Flask app."""

    # 🟢 PostgreSQL Database URL (Render)
    DATABASE_URL = os.getenv("DATABASE_URL",
                             "postgresql://library_user:IWKqxVgpsegDHkkXp6WDAmP20buZGvxn@dpg-cvlq570dl3ps739u14hg-a.oregon-postgres.render.com/library_db_ipjn")

    if not DATABASE_URL:
        raise ValueError("❌ DATABASE_URL Not Found! Check your environment variables.")

    # 🟢 SQLAlchemy Configuration
    SQLALCHEMY_DATABASE_URI = DATABASE_URL + "?sslmode=require"  # SSL required for Render
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable tracking for better performance

    # 🟢 Secret Key for Flask (Use for Sessions, CSRF Protection, etc.)
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")

    # 🟢 Other Configurations (Modify as needed)
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"  # Toggle debug mode
