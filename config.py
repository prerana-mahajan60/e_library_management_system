import os
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration settings for Flask app."""

    # Get the DATABASE_URL from environment
    db_url = os.getenv("DATABASE_URL")

    if not db_url:
        raise ValueError("❌ DATABASE_URL not found! Please check your .env file.")

    # Fix old Heroku-style URL if needed
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    # Flask settings
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")

    # Convert DEBUG from string to bool
    DEBUG = os.getenv("DEBUG", "False").strip().lower() in ("true", "1", "yes")
