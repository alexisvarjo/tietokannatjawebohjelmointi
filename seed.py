import random
import time
import sqlite3

db = sqlite3.connect("database.db")

db.execute("DELETE FROM users")
db.execute("DELETE FROM posts")
db.execute("DELETE FROM messages")
db.execute("DELETE FROM pictures")
db.execute("DELETE FROM prices")

user_count = 10**7
post_count = 10**6
message_count = 10**7

for i in range(1, user_count + 1):
    db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
               ["user" + str(i), "hash" + str(i)])
    print("user count", i)

for i in range(1, post_count + 1):
    user_id = random.randint(1, user_count)
    cursor = db.execute("INSERT INTO posts (title, user_id, type, content) VALUES (?, ?, ?, ?)",
                        ["post" + str(i), user_id, "regular", "content for post " + str(i)])
    picture_data = bytes([random.randint(0, 255) for _ in range(100)])
    db.execute("INSERT INTO pictures (post_id, picture) VALUES (?, ?)",
               [cursor.lastrowid, picture_data])
    random_price = random.uniform(1, 1000)
    db.execute("INSERT INTO prices (post_id, price, type) VALUES (?, ?, ?)",
               [cursor.lastrowid, random_price, "regular"])
    print("post count", i)

for i in range(1, message_count + 1):
    user_id = random.randint(1, user_count)
    post_id = random.randint(1, post_count)
    db.execute("""INSERT INTO messages (content, sent_at, user_id, post_id)
                  VALUES (?, datetime('now'), ?, ?)""",
               ["message" + str(i), user_id, post_id])
    print("message count", i)

db.commit()
db.close()
