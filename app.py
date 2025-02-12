import sqlite3
from flask import Flask
from flask import redirect, render_template, request
from flask import session
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import db
import config
import posts

app = Flask(__name__)

app.secret_key = config.secret_key

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return "VIRHE: salasanat eivät ole samat"
    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return "VIRHE: tunnus on jo varattu"

    return render_template("register_success.html")


@app.route("/")
def index():
    threads = posts.get_posts()
    return render_template("index.html", threads=threads)

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    sql = "SELECT id, password_hash FROM users WHERE username = ?"
    result = db.query(sql, [username])

    if not result:
        return "VIRHE: väärä tunnus tai salasana"

    user_id, password_hash = result[0]

    if check_password_hash(password_hash, password):
        session["username"] = username
        session["user_id"] = user_id  # Ensure user ID is added to the session
        return redirect("/")
    else:
        return "VIRHE: väärä tunnus tai salasana"


@app.route("/logout")
def logout():
    session.clear()  # Clears the entire session
    return redirect("/")


@app.route("/new_thread", methods=["POST", "GET"])
def new_thread():
    if request.method == "GET":
        return render_template("new_thread.html")

    title = request.form["title"]
    content = request.form["content"]
    type = request.form["category"]
    user_id = session["user_id"]

    thread_id = posts.add_thread(title, content, user_id, type)
    return redirect("/thread/" + str(thread_id))

@app.route("/thread/<int:thread_id>")
def show_thread(thread_id):
    thread = posts.get_thread(thread_id)
    messages = posts.get_messages(thread_id)
    return render_template("thread.html", thread=thread, messages=messages)

@app.route("/edit/<int:message_id>", methods=["GET", "POST"])
def edit_message(message_id):
    message = posts.get_message(message_id)

    if request.method == "GET":
        return render_template("edit.html", message=message)

    if request.method == "POST":
        content = request.form["content"]
        posts.update_message(message["id"], content)
        return redirect("/thread/" + str(message["post_id"]))


@app.route("/search", methods=["POST", "GET"])
def search():
    if request.method == "GET":
        return render_template("search.html")

    if request.method == "POST":
        keyword = request.form["keyword"]
        threads = posts.search(keyword)
        return render_template("search.html", keyword=keyword, threads=threads)


@app.route("/remove/<int:message_id>", methods=["GET", "POST"])
def remove_message(message_id):
    message = posts.get_message(message_id)
    message_count = posts.count_messages(message["post_id"])

    if request.method == "GET":
        return render_template("remove.html", message=message)

    if request.method == "POST":
        if "continue" in request.form:
            posts.remove_message(message["id"])
            if message_count == 1:
                posts.remove_thread(message["post_id"])
                return redirect("/")
            else:
                return redirect("/thread/" + str(message["post_id"]))
        return redirect("/thread/" + str(message["post_id"]))

@app.route("/new_message", methods=["POST"])
def new_message():
    content = request.form["content"]
    user_id = session["user_id"]
    thread_id = request.form["post_id"]

    posts.add_message(content, user_id, thread_id)
    return redirect("/thread/" + str(thread_id))

@app.route("/users", methods=["GET"])
def users():
    users_list = [dict(u) for u in posts.get_users()]
    all_threads = [dict(t) for t in posts.get_user_threads()]

    for user in users_list:
        user['threads'] = []

    for thread in all_threads:
        thread['url'] = f"/thread/{thread['id']}"
        for user in users_list:
            if user["id"] == thread["user_id"]:
                user["threads"].append(thread)
                break

    return render_template("users.html", users=users_list)
