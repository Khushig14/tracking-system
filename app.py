from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


# ---------------- DATABASE INIT ----------------
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


# ---------------- HOME DASHBOARD ----------------
@app.route("/")
def home():

    connection = sqlite3.connect("issues.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    # All issues
    cursor.execute("SELECT * FROM issues ORDER BY id DESC")
    issues = cursor.fetchall()

    # Stats
    cursor.execute("SELECT COUNT(*) FROM issues")
    total_issues = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM issues WHERE status='Open'")
    open_issues = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM issues WHERE status='Resolved'")
    resolved_issues = cursor.fetchone()[0]

    connection.close()

    return render_template(
        "home.html",
        issues=issues,
        total_issues=total_issues,
        open_issues=open_issues,
        resolved_issues=resolved_issues
    )


# ---------------- ADD ISSUE ----------------
@app.route("/add_issue", methods=["GET", "POST"])
def add_issue():

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        severity = request.form["severity"]
        status = request.form["status"]

        connection = sqlite3.connect("issues.db")
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO issues(title, description, severity, status)
            VALUES (?, ?, ?, ?)
        """, (title, description, severity, status))

        connection.commit()
        connection.close()

        return redirect("/")

    return render_template("add_issue.html")


# ---------------- START APP ----------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)