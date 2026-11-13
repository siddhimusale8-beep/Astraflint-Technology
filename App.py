from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = "change-this-secret-key"


# Database Connection
def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


# Create Database Tables
def create_table():

    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS enquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            subject TEXT NOT NULL,
            message TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS internship_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            college TEXT NOT NULL,
            course TEXT NOT NULL,
            internship_duration TEXT NOT NULL,
            domain TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Add created_at if an older table does not have it
    columns = [
        row["name"]
        for row in conn.execute(
            "PRAGMA table_info(internship_applications)"
        ).fetchall()
    ]

    if "created_at" not in columns:
        conn.execute(
            "ALTER TABLE internship_applications ADD COLUMN created_at TEXT"
        )
        conn.execute("""
            UPDATE internship_applications
            SET created_at = datetime('now')
            WHERE created_at IS NULL
        """)

    conn.commit()
    conn.close()


# Home Page
@app.route("/")
@app.route("/home")
def Home():
    return render_template("Home.html")


# About Page
@app.route("/about")
def about():
    return render_template("about.html")


# Services Page
@app.route("/services")
def services():
    return render_template("services.html")


# Projects Page
@app.route("/projects")
def projects():
    return render_template("projects.html")


# Internships Page
@app.route("/internships")
def internships():
    return render_template("internships.html")

# Contact Page
@app.route("/contact", methods=["GET", "POST"])
def contact():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        subject = request.form.get("subject", "").strip()
        message = request.form.get("message", "").strip()

        if not all([name, email, subject, message]):
            return "Please fill in all required fields.", 400

        conn = get_db_connection()

        conn.execute("""
            INSERT INTO enquiries (name, email, subject, message)
            VALUES (?, ?, ?, ?)
        """, (name, email, subject, message))

        conn.commit()
        conn.close()

        return render_template("success.html")

    return render_template("contact.html")
# Admin Login
@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form.get("username", "")
        password = request.form.get("password", "")

        # Existing Admin Credentials
        if username == "admin" and password == "Admin@123":
            session["admin_logged_in"] = True
            return redirect(url_for("admin"))

        return render_template(
            "admin_login.html",
            error="Invalid username or password!"
        )

    return render_template("admin_login.html")


# Admin Dashboard
@app.route("/admin")
def admin():

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    conn = get_db_connection()

    # Check internship application columns
    columns = [
        row["name"]
        for row in conn.execute(
            "PRAGMA table_info(internship_applications)"
        ).fetchall()
    ]

    # Add status column if it does not exist
    if "status" not in columns:
        conn.execute("""
            ALTER TABLE internship_applications
            ADD COLUMN status TEXT NOT NULL DEFAULT 'Pending'
        """)

    conn.commit()

    enquiries = conn.execute(
        "SELECT * FROM enquiries ORDER BY id ASC"
    ).fetchall()

    applications = conn.execute(
        "SELECT * FROM internship_applications ORDER BY id ASC"
    ).fetchall()

    conn.close()

    return render_template(
        "admin.html",
        enquiries=enquiries,
        applications=applications
    )
# Add status column if it does not exist
    columns = [
    row["name"]
    for row in conn.execute(
        "PRAGMA table_info(internship_applications)"
    ).fetchall()
    ]

    if "status" not in columns:
      conn.execute("""
        ALTER TABLE internship_applications
        ADD COLUMN status TEXT NOT NULL DEFAULT 'Pending'
    """)

    conn.commit()

    return render_template(
        "admin.html",
        enquiries=enquiries,
        applications=applications
    )

# Update Internship Application Status
@app.route("/admin/update-application/<int:id>", methods=["POST"])
def update_application_status(id):

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    status = request.form.get("status", "")

    allowed_status = ["Pending", "Approved", "Rejected"]

    if status not in allowed_status:
        return redirect(url_for("admin") + "#applications")

    conn = get_db_connection()

    conn.execute("""
        UPDATE internship_applications
        SET status = ?
        WHERE id = ?
    """, (status, id))

    conn.commit()
    conn.close()

    return redirect(url_for("admin") + "#applications")

# View Contact Enquiry
@app.route("/admin/enquiry/<int:id>")
def view_enquiry(id):

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    conn = get_db_connection()

    record = conn.execute(
        "SELECT * FROM enquiries WHERE id = ?", (id,)
    ).fetchone()

    conn.close()

    if record is None:
        return "Enquiry not found.", 404

    return render_template(
        "admin_view.html",
        title="Contact Enquiry",
        record=record
    )


# Delete Contact Enquiry
@app.route("/admin/delete-enquiry/<int:id>", methods=["POST"])
def delete_enquiry(id):

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM enquiries WHERE id = ?", (id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("admin"))


# View Internship Application
@app.route("/admin/application/<int:id>")
def view_application(id):

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    conn = get_db_connection()

    record = conn.execute(
        "SELECT * FROM internship_applications WHERE id = ?", (id,)
    ).fetchone()

    conn.close()

    if record is None:
        return "Application not found.", 404

    return render_template(
        "admin_view.html",
        title="Internship Application",
        record=record
    )


# Delete Internship Application
@app.route("/admin/delete-application/<int:id>", methods=["POST"])
def delete_application(id):

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM internship_applications WHERE id = ?", (id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("admin"))


# Internship Application Form
@app.route("/internship-form", methods=["GET", "POST"])
def internship_form():

    # GET - Open Internship Form
    if request.method == "GET":
        return render_template("internship_form.html")

    # POST - Submit Application
    if request.method == "POST":

        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        college = request.form.get("college", "").strip()
        course = request.form.get("course", "").strip()
        duration = request.form.get("duration", "").strip()
        domain = request.form.get("domain", "").strip()

        if not all([
            full_name, email, phone, college,
            course, duration, domain
        ]):
            return "Please fill in all required fields.", 400

        conn = get_db_connection()

        conn.execute("""
            INSERT INTO internship_applications
            (full_name, email, phone, college, course,
             internship_duration, domain)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            full_name,
            email,
            phone,
            college,
            course,
            duration,
            domain
        ))

        conn.commit()
        conn.close()
        return render_template("internship_success.html")

# Admin Logout
@app.route("/admin-logout")
def admin_logout():

    session.pop("admin_logged_in", None)

    return redirect(url_for("admin_login"))


# Privacy Policy
@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


if __name__ == "__main__":

    create_table()

    app.run(debug=True)