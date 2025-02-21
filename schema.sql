CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE posts (
    id INTEGER PRIMARY KEY,
    title TEXT,
    user_id INTEGER REFERENCES users,
    type TEXT,
    content TEXT
);

CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    content TEXT,
    sent_at TEXT,
    user_id INTEGER REFERENCES users,
    post_id INTEGER REFERENCES posts,
    status INTEGER DEFAULT 1
);

CREATE TABLE pictures (
    id INTEGER PRIMARY KEY,
    post_id INTEGER REFERENCES posts,
    picture BLOB
);
