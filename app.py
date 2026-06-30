from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# ---------------- DATABASE ----------------
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
            assigned_to TEXT,
            date_reported DATE,
            cve TEXT,
            remediation TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Add missing columns safely (for existing databases)
    try:
        cursor.execute("ALTER TABLE issues ADD COLUMN assigned_to TEXT")
        cursor.execute("ALTER TABLE issues ADD COLUMN date_reported DATE")
        cursor.execute("ALTER TABLE issues ADD COLUMN cve TEXT")
        cursor.execute("ALTER TABLE issues ADD COLUMN remediation TEXT")
    except sqlite3.OperationalError:
        pass  # Columns already exist

    connection.commit()
    connection.close()

# ---------------- HOME ----------------
@app.route("/")
def home():
    connection = sqlite3.connect("issues.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM issues ORDER BY id DESC")
    issues = cursor.fetchall()

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
        assigned_to = request.form.get("assigned_to")
        date_reported = request.form.get("date_reported")
        cve = request.form.get("cve")
        remediation = request.form.get("remediation")

        connection = sqlite3.connect("issues.db")
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO issues(title, description, severity, status, assigned_to, date_reported, cve, remediation)
            VALUES(?,?,?,?,?,?,?,?)
        """, (title, description, severity, status, assigned_to, date_reported, cve, remediation))

        connection.commit()
        connection.close()

        return redirect("/")

    return render_template("add_issue.html")

# ---------------- VIEW ALL ----------------
@app.route("/issues")
def view_issues():
    connection = sqlite3.connect("issues.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM issues ORDER BY id DESC")
    issues = cursor.fetchall()
    connection.close()
    return render_template("view_issues.html", issues=issues)

# ---------------- VIEW SINGLE ISSUE ----------------
@app.route("/view_issue/<int:id>")
def view_issue(id):
    connection = sqlite3.connect("issues.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM issues WHERE id=?", (id,))
    issue = cursor.fetchone()
    connection.close()
    return render_template("view_issues.html", issue=issue)   # Pass 'issue'

# ---------------- EDIT ----------------
@app.route("/edit_issue/<int:id>", methods=["GET", "POST"])
def edit_issue(id):
    connection = sqlite3.connect("issues.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        severity = request.form["severity"]
        status = request.form["status"]
        assigned_to = request.form.get("assigned_to")
        date_reported = request.form.get("date_reported")
        cve = request.form.get("cve")
        remediation = request.form.get("remediation")

        cursor.execute("""
            UPDATE issues
            SET title=?, description=?, severity=?, status=?,
                assigned_to=?, date_reported=?, cve=?, remediation=?,
                last_updated=CURRENT_TIMESTAMP
            WHERE id=?
        """, (title, description, severity, status, assigned_to, date_reported, cve, remediation, id))

        connection.commit()
        connection.close()
        return redirect("/")

    cursor.execute("SELECT * FROM issues WHERE id=?", (id,))
    issue = cursor.fetchone()
    connection.close()
    return render_template("edit_issues.html", issue=issue)

# ---------------- DELETE ----------------
@app.route("/delete_issue/<int:id>")
def delete_issue(id):
    connection = sqlite3.connect("issues.db")
    cursor = connection.cursor()
    cursor.execute("DELETE FROM issues WHERE id=?", (id,))
    connection.commit()
    connection.close()
    return redirect("/issues")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)