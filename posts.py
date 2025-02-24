import sqlite3
from flask import g
import db
from flask import Flask

def get_posts():
    sql = """
        SELECT p.id,
               p.title,
               p.type AS category,
               COUNT(m.id) AS total,
               MAX(m.sent_at) AS last,
               (SELECT pic.id
                FROM pictures pic
                WHERE pic.post_id = p.id
                ORDER BY pic.id ASC
                LIMIT 1) AS thumbnail,
               (SELECT pr.price
                FROM prices pr
                WHERE pr.post_id = p.id
                ORDER BY pr.id ASC
                LIMIT 1) AS price
        FROM posts p
        LEFT JOIN messages m ON p.id = m.post_id
        GROUP BY p.id
        ORDER BY p.id DESC
    """
    return db.query(sql)



def add_thread(title, content, user_id, type):
    types = {1: "Myynti", 2: "Osto", 3: "Vaihto"}
    post_type = types[int(type)]
    sql = "INSERT INTO posts (title, user_id, type) VALUES (?, ?, ?)"
    db.execute(sql, [title, user_id, post_type])
    thread_id = db.last_insert_id()
    add_message(content, user_id, thread_id)
    return thread_id

def add_message(content, user_id, thread_id):
    sql = """INSERT INTO messages (content, sent_at, user_id, post_id)
             VALUES (?, datetime('now'), ?, ?)"""
    db.execute(sql, [content, user_id, thread_id])


def get_thread(thread_id):
    sql = "SELECT id, title, type AS category FROM posts WHERE id = ?"
    return db.query(sql, [thread_id])[0]


def get_messages(thread_id):
    sql = """SELECT m.id, m.content, m.sent_at, m.user_id, u.username
             FROM messages m, users u
             WHERE m.user_id = u.id AND m.post_id = ?
             ORDER BY m.id"""
    return db.query(sql, [thread_id])

def count_messages(thread_id):
    sql = "SELECT COUNT(id) FROM messages WHERE post_id = ?"
    return db.query(sql, [thread_id])[0][0]

def update_message(message_id, content):
    sql = "UPDATE messages SET content = ? WHERE id = ?"
    db.execute(sql, [content, message_id])

def remove_message(message_id):
    sql = "DELETE FROM messages WHERE id = ?"
    db.execute(sql, [message_id])

def get_message(message_id):
    sql = "SELECT id, content, post_id FROM messages WHERE id = ?"
    result = db.query(sql, [message_id])

    if result:
        return result[0]  # Return the first (and expected to be only) row
    else:
        return None  # Handle the case where no message exists with the given ID

def remove_thread(thread_id):
    sql = "DELETE FROM posts WHERE id = ?"
    db.execute(sql, [thread_id])

def search(keyword):
    sql = """
        SELECT
            posts.id AS id,
            posts.title,
            posts.type AS category,
            COUNT(messages.id) AS total_messages,
            MAX(messages.sent_at) AS last_updated
        FROM posts
        LEFT JOIN messages ON posts.id = messages.post_id
        WHERE posts.title LIKE ? OR messages.content LIKE ?
        GROUP BY posts.id
        ORDER BY last_updated DESC
    """
    return db.query(sql, [f"%{keyword}%", f"%{keyword}%"])


def get_users():
    sql = "SELECT id, username FROM users"
    return db.query(sql)

def get_user_threads():
    sql = """
        SELECT p.id, p.title, p.user_id, p.type AS category, COUNT(m.id) AS message_count
        FROM posts p
        LEFT JOIN messages m ON p.id = m.post_id
        GROUP BY p.id
        ORDER BY p.id DESC
    """
    return db.query(sql)

def add_image(post_id, image):
    sql = "INSERT INTO pictures (post_id, picture) VALUES (?, ?)"
    db.execute(sql, [post_id, image.read()])

def get_pictures(post_id):
    sql = "SELECT id, picture FROM pictures WHERE post_id = ?"
    return db.query(sql, [post_id])

def get_single_picture(picture_id):
    sql = "SELECT picture FROM pictures WHERE id = ?"
    return db.query(sql, [picture_id])

def add_price(post_id, price, type):
    types = {1: "Myynti", 2: "Osto", 3: "Vaihto"}
    post_type = types[int(type)]
    sql = "INSERT INTO prices (post_id, price, type) VALUES (?, ?, ?)"
    db.execute(sql, [post_id, price, post_type])

def get_price(post_id):
    sql = "SELECT price FROM prices WHERE post_id = ?"
    return db.query(sql, [post_id])[0][0]
