from flask import Flask
import sqlite3

app = Flask(__name__)


def init_db():
    connection = sqlite3.connect("issues.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS issues(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            severity TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()

@app.route("/")
def home():
    return "Welcome to the X-Bix TechVentures Issue & Vulnerability Tracking API"

if __name__ == "__main__":
    app.run(debug=True)