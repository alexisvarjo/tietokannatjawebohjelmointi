import sqlite3
import math
from flask import Flask, abort, Response
from flask import redirect, render_template, request
from flask import session, flash
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import db
import config
import posts

app = Flask(__name__)

app.secret_key = config.secret_key

@app.route("/create", methods=["POST", "GET"])
def create(filled={}):
    if request.method == "GET":
        return render_template("register.html", filled=filled)

    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]

        filled = {"username": username, "password1": password1, "password2": password2}

        if not username or len(username) > 50:
            flash("VIRHE: Käyttäjänimi on tyhjä tai yli 50 merkkiä")
            return render_template("register.html", filled=filled)
        if not password1 or len(password1) > 100:
            flash("VIRHE: Salasana on tyhjä tai yli 100 merkkiä")
            return render_template("register.html", filled=filled)
        if not password2 or len(password2) > 100:
            flash("VIRHE: Salasana on tyhjä tai yli 100 merkkiä")
            return render_template("register.html", filled=filled)
        if password1 != password2:
            flash("VIRHE: Salasanat eivät täsmää")
            return render_template("register.html", filled=filled)

        password_hash = generate_password_hash(password1)

        try:
            sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
            db.execute(sql, [username, password_hash])
        except sqlite3.IntegrityError:
            flash("VIRHE: Tunnus on jo varattu")
            return redirect("/create")

        return render_template("register_success.html")


@app.route("/")
@app.route("/<int:page>")
def index(page=1):
    page_size = 10
    thread_count = posts.thread_count()
    page_count = math.ceil(thread_count / page_size)
    page_count = max(page_count, 1)
    if page < 1:
        return redirect("/1")
    if page > page_count:
        return redirect("/"+str(page_count))

    threads = posts.get_posts(page, page_size)
    return render_template("index.html", threads=threads, page=page, page_count=page_count)


@app.route("/login", methods=["POST", "GET"])
def login(filled={}):
    if request.method == "GET":
        return render_template("login.html")

    username = request.form["username"]
    password = request.form["password"]
    filled = {"username": username}
    if not username or len(username) > 50:
        flash("VIRHE: Käyttäjänimi puuttuu tai on liian pitkä")
        return redirect("/login")
    if not password or len(password) > 100:
        flash("VIRHE: Salasana puuttuu tai on liian pitkä")
        return render_template("login.html", filled=filled)

    sql = "SELECT id, password_hash FROM users WHERE username = ?"
    result = db.query(sql, [username])

    if not result:
        flash("VIRHE: Salasana tai käyttäjänimi on väärä")
        return redirect("/login")

    user_id, password_hash = result[0]

    if check_password_hash(password_hash, password):
        session["username"] = username
        session["user_id"] = user_id  # Ensure user ID is added to the session
        session["csrf_token"] = secrets.token_hex(16)
        return redirect("/")
    else:
        flash("VIRHE: Salasana tai käyttäjänimi on väärä")
        return redirect("/login")


@app.route("/logout")
def logout():
    session.clear()  # Clears the entire session
    return redirect("/")


@app.route("/new_thread", methods=["POST", "GET"])
def new_thread(filled={}):
    require_login()
    check_csrf()
    if request.method == "GET":
        return render_template("new_thread.html")

    price = int(request.form["price"])
    title = request.form["title"]
    content = request.form["content"]
    type = request.form["category"]
    user_id = session["user_id"]
    images = request.files.getlist("images")
    filled = {"price": price, "title": title, "content": content, "type": type, "user_id": user_id}

    if len(images) == 0:
        flash("VIRHE: Valitse vähintään yksi kuva")
        return render_template("new_thread.html", filled)

    if not title or len(title) > 100:
        flash("VIRHE: Otsikko puuttuu tai on yli 100 merkkiä pitkä")
        if title:
            filled["title"] = title[0:99]
        return render_template("new_thread.html", filled)
    if not content or len(content) > 2000:
        if content:
            filled["content"] = content[0:1999]
        flash("VIRHE: Sisältö puuttuu tai on yli 2000 merkkiä pitkä")
        return render_template("new_thread.html", filled)
    if not type or type not in ["1", "2", "3"]:
        flash("VIRHE: Valitse kategoria")
        return redirect("/new_thread")

    if not price or price < 0:
        flash("VIRHE: Hinta puuttuu tai on negatiivinen")
        return render_template("new_thread.html", title=title, content=content, category=type)

    if "last_thread" in session and session["last_thread"] == (title, content, type):
        flash("VIRHE: Sama viesti on jo lähetetty")
        return redirect("/")
    else:
        print(title, content, type, user_id)
        thread_id = posts.add_thread(title, content, user_id, type)
        price = posts.add_price(thread_id, price, type)
        for image in images:
            posts.add_image(thread_id, image)
        session["last_thread"] = (title, content, type)
        return redirect("/thread/" + str(thread_id))

@app.route("/thread/<int:thread_id>")
def show_thread(thread_id):
    thread = posts.get_thread(thread_id)
    if not thread:
        abort(404)
    messages = posts.get_messages(thread_id)
    pictures = posts.get_pictures(thread_id)
    price = posts.get_price(thread_id)
    return render_template("thread.html", thread=thread, messages=messages, pictures=pictures, price=price)

@app.route("/picture/<int:picture_id>")
def serve_picture(picture_id):
    row = posts.get_single_picture(picture_id)
    if not row:
        abort(404)

    # Return the image bytes with the appropriate MIME type.
    return Response(row[0], mimetype="image/png")


@app.route("/edit/<int:message_id>", methods=["GET", "POST"])
def edit_message(message_id):
    require_login()
    check_csrf()
    message = posts.get_message(message_id)
    if message["user_id"] != session["user_id"]:
        abort(403)
    if request.method == "GET":
        return render_template("edit.html", message=message)

    if request.method == "POST":
        content = request.form["content"]

        if not content or len(content) > 2000:
            flash("VIRHE: Sisältö puuttuu tai on liian pitkä")
            return redirect("/edit/" + str(message_id))

        posts.update_message(message["id"], content)
        return redirect("/thread/" + str(message["post_id"]))


@app.route("/search", methods=["POST", "GET"])
def search():
    if request.method == "GET":
        return render_template("search.html")

    if request.method == "POST":
        keyword = request.form["keyword"]

        if not keyword or len(keyword) > 200:
            flash("VIRHE: Hakusana puuttuu tai on liian pitkä")
            return redirect("/search")

        threads = posts.search(keyword)
        return render_template("search.html", keyword=keyword, threads=threads)


@app.route("/remove/<int:message_id>", methods=["GET", "POST"])
def remove_message(message_id):
    require_login()
    check_csrf()
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
    require_login()
    check_csrf()
    content = request.form["content"]
    user_id = session["user_id"]
    thread_id = request.form["post_id"]

    if not content or len(content) > 2000:
        thread = posts.get_thread(thread_id)
        messages = posts.get_messages(thread_id)
        flash("VIRHE: Viesti puuttuu tai on liian pitkä")
        return redirect("/new_message")

    if "last_message" in session and session["last_message"] == (content, thread_id):
        thread = posts.get_thread(thread_id)
        messages = posts.get_messages(thread_id)
        flash("VIRHE: Sama viesti on jo lähetetty")
        return redirect("/thread/" + str(thread_id))
    else:
        try:
            posts.add_message(content, user_id, thread_id)
            session["last_message"] = (content, thread_id)
        except sqlite3.IntegrityError:
            abort(403)
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

@app.route("/about", methods=["GET"])
def about():
    return render_template("about.html")

def require_login():
    if "user_id" not in session:
        abort(403)

@app.route("/user/<int:user_id>")
def show_user(user_id):
    user = posts.get_user(user_id)
    if not user:
        abort(404)
    messages = posts.get_messages(user_id)
    return render_template("user.html", user=user, messages=messages)

def check_csrf():
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)
