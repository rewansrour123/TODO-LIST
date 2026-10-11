
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)
import pymysql
import os
import re
import bcrypt
from dotenv import load_dotenv


# =================================================
# Load environment variables
# =================================================

load_dotenv()


# =================================================
# Create Flask application
# =================================================

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")

if not app.secret_key:
    raise RuntimeError("SECRET_KEY is missing from the .env file")


# =================================================
# MySQL Connection
# =================================================

def get_db_connection():

    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        cursorclass=pymysql.cursors.DictCursor
    )


# =================================================
# Helper: validate email
# =================================================

def valid_email(email):

    return bool(
        re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+",
            email
        )
    )


# =================================================
# Helper: get current user's todos
# =================================================

def get_user_todos(user_id):

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT todo_id, title, is_done, created_at
                FROM todos
                WHERE user_id = %s
                ORDER BY todo_id DESC
                """,
                (user_id,)
            )

            return cursor.fetchall()

    finally:
        connection.close()


# =================================================
# HOME / TO-DO LIST
# =================================================

@app.route("/")
def home():

    if "user_id" not in session:
        return redirect(url_for("login"))

    todos = get_user_todos(session["user_id"])

    return render_template(
        "todos.html",
        todos=todos,
        user_name=session["user_name"]
    )


# =================================================
# REGISTER - GET
# =================================================

@app.route("/register", methods=["GET"])
def register():

    return render_template("register.html")


# =================================================
# REGISTER - POST
# =================================================

@app.route("/register", methods=["POST"])
def register_post():

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    # Server-side validation

    if not name:
        flash("Name is required", "error")
        return redirect(url_for("register"))

    if len(name) > 100:
        flash("Name is too long", "error")
        return redirect(url_for("register"))

    if not email:
        flash("Email is required", "error")
        return redirect(url_for("register"))

    if not valid_email(email):
        flash("Please enter a valid email", "error")
        return redirect(url_for("register"))

    if not password.strip():
        flash("Password is required", "error")
        return redirect(url_for("register"))

    if not confirm_password.strip():
        flash("Confirm password is required", "error")
        return redirect(url_for("register"))

    if password != confirm_password:
        flash("Passwords do not match", "error")
        return redirect(url_for("register"))

    # Hash password

    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    connection = get_db_connection()

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO users (email, name, password_hash)
                VALUES (%s, %s, %s)
                """,
                (email, name, password_hash)
            )

            connection.commit()

            user_id = cursor.lastrowid

    except pymysql.err.IntegrityError:

        connection.rollback()

        flash("Email Already Exists", "error")
        return redirect(url_for("register"))

    finally:
        connection.close()

    # Log in the new user

    session.clear()
    session["user_id"] = user_id
    session["user_name"] = name

    return redirect(url_for("home"))


# =================================================
# LOGIN - GET
# =================================================

@app.route("/login", methods=["GET"])
def login():

    return render_template("login.html")


# =================================================
# LOGIN - POST
# =================================================

@app.route("/login", methods=["POST"])
def login_post():

    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    # Server-side validation

    if not email:
        flash("Email is required", "error")
        return redirect(url_for("login"))

    if not valid_email(email):
        flash("Please enter a valid email", "error")
        return redirect(url_for("login"))

    if not password.strip():
        flash("Password is required", "error")
        return redirect(url_for("login"))

    connection = get_db_connection()

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT user_id, name, password_hash
                FROM users
                WHERE email = %s
                """,
                (email,)
            )

            user = cursor.fetchone()

    finally:
        connection.close()

    # Use the same error for an unknown email or wrong password

    if user is None:
        flash("Invalid email or password", "error")
        return redirect(url_for("login"))

    password_correct = bcrypt.checkpw(
        password.encode("utf-8"),
        user["password_hash"].encode("utf-8")
    )

    if not password_correct:
        flash("Invalid email or password", "error")
        return redirect(url_for("login"))

    # Login successful

    session.clear()
    session["user_id"] = user["user_id"]
    session["user_name"] = user["name"]

    return redirect(url_for("home"))


# =================================================
# ADD TO-DO
# =================================================

@app.route("/todo/add", methods=["POST"])
def add_todo():

    if "user_id" not in session:
        return redirect(url_for("login"))

    title = request.form.get("title", "").strip()

    # Server-side validation

    if not title:
        flash("Title is required", "error")
        return redirect(url_for("home"))

    if len(title) > 200:
        flash("Title is too long", "error")
        return redirect(url_for("home"))

    user_id = session["user_id"]

    connection = get_db_connection()

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO todos (user_id, title)
                VALUES (%s, %s)
                """,
                (user_id, title)
            )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

    return redirect(url_for("home"))


# =================================================
# EDIT TO-DO
# =================================================

@app.route("/todo/edit/<int:todo_id>", methods=["POST"])
def edit_todo(todo_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    title = request.form.get("title", "").strip()

    # Server-side validation

    if not title:
        flash("Title is required", "error")
        return redirect(url_for("home"))

    if len(title) > 200:
        flash("Title is too long", "error")
        return redirect(url_for("home"))

    user_id = session["user_id"]

    connection = get_db_connection()

    try:

        with connection.cursor() as cursor:

            # Update only a task belonging to this user

            cursor.execute(
                """
                UPDATE todos
                SET title = %s
                WHERE todo_id = %s AND user_id = %s
                """,
                (title, todo_id, user_id)
            )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

    return redirect(url_for("home"))


# =================================================
# MARK TO-DO AS DONE / UNDONE
# =================================================

@app.route("/todo/toggle/<int:todo_id>", methods=["POST"])
def toggle_todo(todo_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    connection = get_db_connection()

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT is_done
                FROM todos
                WHERE todo_id = %s AND user_id = %s
                """,
                (todo_id, user_id)
            )

            todo = cursor.fetchone()

            if todo is None:
                return redirect(url_for("home"))

            new_status = (
                0 if todo["is_done"] == 1 else 1
            )

            cursor.execute(
                """
                UPDATE todos
                SET is_done = %s
                WHERE todo_id = %s AND user_id = %s
                """,
                (new_status, todo_id, user_id)
            )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

    return redirect(url_for("home"))


# =================================================
# DELETE TO-DO
# =================================================

@app.route("/todo/delete/<int:todo_id>", methods=["POST"])
def delete_todo(todo_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    connection = get_db_connection()

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                DELETE FROM todos
                WHERE todo_id = %s AND user_id = %s
                """,
                (todo_id, user_id)
            )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

    return redirect(url_for("home"))


# =================================================
# LOGOUT
# =================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# =================================================
# RUN FLASK
# =================================================

if __name__ == "__main__":
    app.run(debug=True)
