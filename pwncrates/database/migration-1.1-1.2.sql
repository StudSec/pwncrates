CREATE TABLE IF NOT EXISTS pwncrates (
    name VARCHAR(64),
    version FLOAT
);

UPDATE pwncrates SET version = 1.2 WHERE version = 1.1 AND name = 'pwncrates';

CREATE TABLE admins (
    user_id INTEGER PRIMARY KEY,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE hidden_users (
    user_id INTEGER PRIMARY KEY,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- need to remove this, just for testing purpose
INSERT into admins values(2);
