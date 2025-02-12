import sqlite3
from flask import g
import db
from flask import Flask



def get_posts():
    sql = """
        SELECT p.id, p.title, COUNT(m.id) AS total, MAX(m.sent_at) AS last
        FROM posts p
        LEFT JOIN messages m ON p.id = m.post_id
        GROUP BY p.id
        ORDER BY p.id DESC
    """
    return db.query(sql)



def add_thread(title, content, user_id, type):
    sql = "INSERT INTO posts (title, user_id, type) VALUES (?, ?, ?)"
    db.execute(sql, [title, user_id, type])
    thread_id = db.last_insert_id()
    add_message(content, user_id, thread_id)
    return thread_id

def add_message(content, user_id, thread_id):
    sql = """INSERT INTO messages (content, sent_at, user_id, post_id)
             VALUES (?, datetime('now'), ?, ?)"""
    db.execute(sql, [content, user_id, thread_id])


def get_thread(thread_id):
    sql = "SELECT id, title FROM posts WHERE id = ?"
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
            posts.id AS post_id,
            posts.title,
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
        SELECT p.id, p.title, p.user_id, COUNT(m.id) AS message_count
        FROM posts p
        LEFT JOIN messages m ON p.id = m.post_id
        GROUP BY p.id
        ORDER BY p.id DESC
    """
    return db.query(sql)
