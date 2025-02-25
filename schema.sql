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

CREATE TABLE pictures (
    id INTEGER PRIMARY KEY,
    post_id INTEGER REFERENCES posts ON DELETE CASCADE,
    picture BLOB
);

CREATE TABLE prices (
    id INTEGER PRIMARY KEY,
    post_id INTEGER REFERENCES posts ON DELETE CASCADE,
    price REAL,
    type TEXT
);

CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    content TEXT,
    sent_at TEXT,
    user_id INTEGER REFERENCES users,
    post_id INTEGER REFERENCES posts,
    status INTEGER DEFAULT 1
);

-- messages
CREATE INDEX idx_messages_post_id_id ON messages (post_id, id);

CREATE INDEX idx_messages_user_id_sent_at ON messages (user_id, sent_at);

-- pictures
CREATE INDEX idx_pictures_post_id_id ON pictures (post_id, id);

-- prices
CREATE INDEX idx_prices_post_id_id ON prices (post_id, id);

-- posts (only if you regularly filter by user_id)
CREATE INDEX idx_posts_user_id ON posts (user_id);
