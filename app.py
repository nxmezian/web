from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from flask import url_for
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
import sqlite3
from cs50 import SQL
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


app = Flask(__name__)

app.static_folder = 'static'

app.secret_key = 'your_secret_key_here'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Initialize variable for current time
now = datetime.now()

# Initialize Flask login manager
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

class User(UserMixin):
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username
        self.authenticated = True

class ThreadForm(FlaskForm):
    thread_title = StringField('Thread Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/forum")
def forum():
    # Connect to the SQLite database
    conn = sqlite3.connect('forum.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM subforums")
    subforum_data = cursor.fetchall()
    cursor.execute("SELECT * FROM threads")
    thread_data = cursor.fetchall()
    cursor.execute("SELECT * FROM posts")
    post_data = cursor.fetchall()
    conn.close()

    # Pass the retrieved posts to a Jinja template for rendering
    return render_template("forum.html", subforums=subforum_data,threads=thread_data, posts=post_data)

@app.route("/subforum/<int:subforum_id>")
def subforum(subforum_id):
    # Connect to the SQLite database
    conn = sqlite3.connect('forum.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM threads WHERE subforum_id=?", (subforum_id,))
    thread_data = cursor.fetchall()
    cursor.execute("SELECT * FROM posts")
    post_data = cursor.fetchall()
    conn.close()

    return render_template("subforum.html", subforum_id=subforum_id, threads=thread_data, posts=post_data)

@app.route('/subforum/<subforum_id>/create_thread', methods=["GET", "POST"])
def create_thread(subforum_id):
    if request.method == "GET":
        return render_template("create_thread.html", subforum_id = subforum_id)
    # process form data and save to database

    elif request.method == "POST":
        thread_title = request.form.get("thread_title")
        subforum = subforum_id
        first_post = request.form.get("first_post")
        conn = sqlite3.connect('forum.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO threads (thread_title, subforum_id) VALUES (?,?)", (thread_title, subforum_id))
        conn.commit()
        cursor.execute("SELECT thread_id FROM threads WHERE thread_title=?", (thread_title,))
        thread_id = cursor.fetchone()[0]
        posted_by = session["username"]
        cursor.execute("INSERT INTO posts (post_content,thread_title, thread_id, posted_by) VALUES(?,?,?,?)", (first_post, thread_title,thread_id,posted_by,))
        conn.commit()
        conn.close()
        return("HEYYY HOW YOU DOIN?")

@app.route("/thread/<int:subforum_id>/<int:thread_id>")
def thread(subforum_id,thread_id):
    # Connect to the SQLite database and find thread info
    conn = sqlite3.connect('forum.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM threads WHERE thread_id=?", (thread_id,))
    thread_data = cursor.fetchone()
    cursor.execute("SELECT * FROM posts WHERE thread_id=?", (thread_id,))
    post_data = cursor.fetchall()
    posted_by = session["username"]
    conn.close()

    # Pass the retrieved posts to a Jinja template for rendering
    return render_template("thread.html", subforum_id = subforum_id,thread_id=thread_id, threads=thread_data, posts=post_data, posted_by=posted_by)

@app.route('/thread/<int:subforum_id>/<int:thread_id>/reply', methods=["GET", "POST"])
def reply(subforum_id, thread_id):
    if request.method == "GET":
        return render_template("create_thread", subforum_id=subforum_id, thread_id=thread_id)
    elif request.method == "POST":
        reply = request.form.get("reply")
        conn =sqlite3.connect("forum.db")
        cursor = conn.cursor()
        posted_by = session["username"]
        cursor.execute("INSERT INTO posts (thread_id, subforum_id, post_content, posted_by) VALUES (?,?,?,?)", (thread_id, subforum_id, reply,posted_by))
        conn.commit()
        conn.close()
        return redirect(url_for('thread', subforum_id=subforum_id, thread_id=thread_id))

@app.route("/zelda_history")
def zelda_history():
    return render_template("zelda_history.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return ("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return ("must provide password", 403)

        # Query database for username
        conn = sqlite3.connect('forum.db')
        cursor = conn.cursor()
        username = request.form.get("username")
        password = request.form.get("password")
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        rows = cursor.fetchone()

        # Ensure username exists and password is correct
        if rows is None:
            return ("Rows is none", 403)

        elif len(rows) != 6 or not check_password_hash(rows[3], password):
            return ("invalid username and/or password", 403)
        else:
            session["user_id"] = rows[0]
            session["username"] =rows[1]
            session["email"] = rows[2]
            session["is_logged_in"] = True
            return redirect("/forum")

    elif request.method == "GET":
        return render_template("login.html")

    else:
        return ("An unknown error has occurred")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    elif request.method =="POST":
        username = request.form.get("username")
        password = request.form.get("password")
        password_repeat = request.form.get("password_repeat")
        hashed_password = generate_password_hash(password)
        email = request.form.get("email")
        registration_date = "now"

        conn = sqlite3.connect("forum.db")
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE username=?", (username,))
        existing_user = cursor

        #if existing_user:
         #   return("Username already exists")

        if not username:
            return ("Please enter a username")

        if not password:
            return ("Please enter a password")

        if password != password_repeat:
            return ("Please match your password in both password fields")

        conn = sqlite3.connect("forum.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username,email,password,registration_date) VALUES(?,?,?,?)", (username,email,hashed_password,registration_date))
        conn.commit()
        conn.close()
        return ("YEAH YEAH WE JUST GOT OUT OF THE TRUCK")

@app.route("/profile")
def profile():
    return render_template("profile.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/forum")

@app.route("/music")
def music():
    return render_template("music.html")

if __name__ == '__main__':
    app.run(debug=True)