from main import app
from config import Config
from flask_sqlalchemy import SQLAlchemy

# To Test Database Connection
try:
    # SQLAlchemy already handles the DB connection via app.config
    with app.app_context():
        connection = app.config['SQLALCHEMY_DATABASE_URI']
        if connection:
            print("Database Connected Successfully!")
        else:
            print("Database Connection Failed!")
except Exception as e:
    print(f"Error: {e}")

# For Running the Application
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
