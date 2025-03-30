import psycopg2
import os


def get_db_connection():
    try:
        #Get DATABASE_URL from Render Environment Variable
        DATABASE_URL = os.environ.get("DATABASE_URL")

        #Connect using Render's PostgreSQL URL
        connection = psycopg2.connect(DATABASE_URL)
        return connection

    except Exception as e:
        print(f" Database Connection Failed: {e}")
        return None
