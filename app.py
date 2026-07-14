from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# DATABASE CREATION
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

    connection.commit()
    connection.close()

# HOME PAGE
@app.route("/")
def home():
    connection = sqlite3.connect("issues.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM issues ORDER BY id ASC")
    issues = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM issues")
    total_issues = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM issues WHERE status='Open'")
    open_issues = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM issues WHERE status='In Progress'")
    in_progress_issues = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM issues WHERE status='Resolved'")
    resolved_issues = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM issues WHERE status='Closed'")
    closed_issues = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM issues WHERE severity='Low'")
    low_severity = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM issues WHERE severity='Medium'")
    medium_severity = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM issues WHERE severity='High'")
    high_severity = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM issues WHERE severity='Critical'")
    critical_severity = cursor.fetchone()[0]
    
    connection.close()

    return render_template(
        "home.html",
        issues=issues,
        total_issues=total_issues,
        open_issues=open_issues,
        in_progress_issues=in_progress_issues,
        resolved_issues=resolved_issues,
        closed_issues=closed_issues,
        low_severity=low_severity,
        medium_severity=medium_severity,
        high_severity=high_severity,
        critical_severity=critical_severity
    )

# ADD ISSUE PAGE
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

# VIEW ALL ISSUES PAGE
@app.route("/issues")
def view_issues():
    # Get search and filter values from URL
    search = request.args.get('search', '').strip()
    severity_filter = request.args.get('severity', '')
    status_filter = request.args.get('status', '')

    connection = sqlite3.connect("issues.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    query = "SELECT * FROM issues WHERE 1=1"
    params = []

    if search:
        query += " AND (title LIKE ? OR description LIKE ? OR cve LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

    if severity_filter:
        query += " AND severity = ?"
        params.append(severity_filter)

    if status_filter:
        query += " AND status = ?"
        params.append(status_filter)

    query += " ORDER BY id DESC"

    cursor.execute(query, params)
    issues = cursor.fetchall()
    connection.close()

    return render_template("view_issues.html", issues=issues, search=search, severity_filter=severity_filter, status_filter=status_filter)

# VIEW SINGLE ISSUE PAGE
@app.route("/view_issue/<int:id>")
def view_issue(id):
    connection = sqlite3.connect("issues.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM issues WHERE id=?", (id,))
    issue = cursor.fetchone()
    connection.close()
    return render_template("view_single_issue.html", issue=issue)   

# EDIT ISSUE PAGE
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

# DELETE ISSUE PAGE
@app.route("/delete_issue/<int:id>")
def delete_issue(id):
    connection = sqlite3.connect("issues.db")
    cursor = connection.cursor()
    cursor.execute("DELETE FROM issues WHERE id=?", (id,))
    connection.commit()
    connection.close()
    return redirect("/")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)