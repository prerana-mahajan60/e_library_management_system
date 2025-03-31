import psycopg2
import os
from dotenv import load_dotenv

# 🟢 Load Secret File from /etc/secrets/.env
load_dotenv("/etc/secrets/.env")

def get_db_connection():
    try:
        # 🟢 Get DATABASE_URL from Secret File
        DATABASE_URL = os.environ.get("DATABASE_URL")

        if not DATABASE_URL:
            raise ValueError("❌ DATABASE_URL Not Found! Check Secret File!")

        # 🟢 Connect using Render's PostgreSQL URL
        connection = psycopg2.connect(DATABASE_URL)
        return connection

    except psycopg2.OperationalError as e:
        print(f"🚨 Database Connection Failed: {e}")
        return None
    except Exception as e:
        print(f"⚠️ Unexpected Error: {e}")
        return None
