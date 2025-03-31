import psycopg2
import os


def get_db_connection():
    try:
        # 🟢 Get DATABASE_URL from Render Environment Variable
        DATABASE_URL = os.environ.get("DATABASE_URL")

        if not DATABASE_URL:
            raise ValueError("❌ DATABASE_URL Not Found! Check Environment Variables!")

        # 🟢 Connect using Render's PostgreSQL URL
        connection = psycopg2.connect(DATABASE_URL)

        # 🟢 Return the connection
        return connection

    except psycopg2.OperationalError as e:
        print(f"🚨 Database Connection Failed: {e}")
        return None
    except Exception as e:
        print(f"⚠️ Unexpected Error: {e}")
        return None
