-- Update challenge table to have uuid
ALTER TABLE challenges ADD COLUMN uuid TEXT;
UPDATE challenges SET uuid = CAST(id AS TEXT);

-- Create table for URLs (challenge id, string)
CREATE TABLE challenge_urls (
    challenge_id INTEGER NOT NULL,
    url TEXT NOT NULL,
    FOREIGN KEY(challenge_id) REFERENCES challenges(id)
);

-- Create table for flags (challenge uuid, flag, points)
CREATE TABLE challenge_flags (
    challenge_id INTEGER NOT NULL,
    flag TEXT NOT NULL,
    FOREIGN KEY(challenge_id) REFERENCES challenges(id)
);

-- Move challenge data to URLs and flags
INSERT INTO challenge_urls (challenge_id, url)
SELECT id, url FROM challenges WHERE url IS NOT NULL;

INSERT INTO challenge_flags (challenge_id, flag)
SELECT id, flag FROM challenges;

-- Remove challenge URLs and flags from challenge data
PRAGMA foreign_keys=off;

CREATE TABLE challenges_new (
    id INTEGER PRIMARY KEY,
    uuid TEXT,
    name VARCHAR(128),
    description VARCHAR(2048),
    category TEXT,
    difficulty INTEGER,
    points INTEGER NOT NULL,
    CONSTRAINT unique_constraint UNIQUE (uuid)
);

INSERT INTO challenges_new (id, name, description, category, difficulty, points)
SELECT id, name, description, category, difficulty, points FROM challenges;

DROP TABLE challenges;
ALTER TABLE challenges_new RENAME TO challenges;

PRAGMA foreign_keys=on;

-- Update category (uuid, name, parent)
CREATE TABLE categories_new (
    id INTEGER PRIMARY KEY,
    uuid TEXT,
    name TEXT NOT NULL,
    description VARCHAR(1024) DEFAULT NULL,
    parent_id TEXT DEFAULT NULL,
    FOREIGN KEY(parent_id) REFERENCES categories_new(id),
    CONSTRAINT unique_constraint UNIQUE (uuid)
);

INSERT INTO categories_new (id, name, description, parent_id)
SELECT id, name, description, parent FROM categories;

DROP TABLE categories;
ALTER TABLE categories_new RENAME TO categories;

-- Set next version
UPDATE pwncrates SET version = 1.3 WHERE version = 1.2 AND name = 'pwncrates';
