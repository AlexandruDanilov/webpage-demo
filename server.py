from flask import Flask, request, render_template, redirect, session, url_for
import os
from werkzeug.utils import secure_filename


# Note: static folder means all files from there will be automatically served over HTTP
app = Flask(__name__, static_folder="public")
app.secret_key = "TODO_task3"

# TODO Task 02: you can use a global variable for storing the auth session
# e.g., add the "authenticated" (boolean) and "username" (string) keys.
# you can use a dict as user/pass database

ALLOWED_USERS = {
    "test": "test123",
    "admin": "n0h4x0rz-plz",
    "dani": "lalala",
}

PROFILE_PIC_FOLDER = os.path.join(app.static_folder, 'images', 'profile')

os.makedirs(PROFILE_PIC_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Task 04: database filename
DATABASE_FILE = "database.txt"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/second")
def second():
    return render_template("second.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    error_msg = ""
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if username in ALLOWED_USERS and ALLOWED_USERS[username] == password:
            session["authenticated"] = True
            session["username"] = username
            return redirect(url_for("index"))
        else:
            error_msg = "Invalid username or password."

    return render_template("login.html", error_msg=error_msg)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.context_processor
def inject_template_vars():
    return {
        "authenticated": session.get("authenticated", False),
        "username": session.get("username", "")
    }



# You can use this as a starting point for Task 04
# (note: you need a "write" counterpart)
def read_database(filename):
    """Reads the user account details from the database file (line by line)."""
    try:
        with open(filename, "rt") as f:
            first_name = f.readline().strip()
            last_name = f.readline().strip()
            age = int(f.readline().strip())
        return {
            "first_name": first_name,
            "last_name": last_name,
            "age": age,
        }
    except Exception as e:
        return {
            "first_name": "",
            "last_name": "",
            "age": 0,
        }


@app.route("/account-details", methods=["GET", "POST"])
def save_account():
    if not session.get("authenticated", False):
        return redirect(url_for("login"))

    # Load data if any (GET request)
    try:
        data = read_database(DATABASE_FILE)
    except Exception:
        data = {"first_name": "", "last_name": "", "age": 0}

    profile_picture = None

    if request.method == "POST":
        # Save form data
        first_name = request.form.get("first_name", "")
        last_name = request.form.get("last_name", "")
        age = request.form.get("age", "0")

        with open(DATABASE_FILE, "wt") as f:
            f.write(f"{first_name.strip()}\n")
            f.write(f"{last_name.strip()}\n")
            f.write(f"{int(age)}\n")

        # Handle file upload
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                profile_picture = filename
                file.save(os.path.join(PROFILE_PIC_FOLDER, filename))

        return redirect(url_for("save_account"))

    # If GET, load data and render form
    return render_template("account-details.html", **data, profile_picture=profile_picture)



@app.errorhandler(404)
def error404(code):
    return (
        "<div style='background-color:red;color:white;font-weight:bold;padding:2rem;'>"
        "HTTP Error 404 - Page Not Found"
        "</div>",
        404,
    )



# Run the webserver (port 5000 - the default Flask port)
if __name__ == "__main__":
    app.run(debug=True, port=5000)

