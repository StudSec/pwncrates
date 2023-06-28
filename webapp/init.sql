-- Initialization file, gets called once on database creation. --

CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name VARCHAR(64),
    password VARCHAR(64),
    email VARCHAR(64) UNIQUE NOT NULL,
    university_id INTEGER DEFAULT 1,
    discord_id VARCHAR(18) DEFAULT NULL,
    points INTEGER DEFAULT 0
);

CREATE TABLE universities (
    id INTEGER PRIMARY KEY,
    name VARCHAR(128)
);

CREATE TABLE solves (
    id INTEGER PRIMARY KEY,
    challenge_id INTEGER,
    solved_time INTEGER,  -- Using unix timestamp over builtin datetime because it feels easier to work with - Aidan
    user_id INTEGER,
    CONSTRAINT unique_constraint UNIQUE (user_id, challenge_id)
);

CREATE TABLE challenges (
    id INTEGER PRIMARY KEY,
    name VARCHAR(128) UNIQUE,    -- challenge names have to be unique, likely not an issue but if it is we need to update the git hook in databases.py
    description VARCHAR(2048),
    points INTEGER,
    category VARCHAR(64),
    difficulty INTEGER,
    subcategory VARCHAR(64),
    flag VARCHAR(128),
    solves INTEGER DEFAULT 0,
    url VARCHAR(128) DEFAULT NULL
);

CREATE TABLE writeups(
    id INTEGER PRIMARY KEY,
    challenge_id INTEGER,
    user_id INTEGER,
    file_name VARCHAR(256),
    CONSTRAINT unique_constraint UNIQUE (challenge_id, user_id)
);

CREATE TABLE categories(
    id INTEGER PRIMARY KEY,
    name VARCHAR(128),
    description VARCHAR(1024) DEFAULT NULL,
    parent INT DEFAULT NULL,     -- The parent category, if not a subcategory will be the same as name --
    CONSTRAINT unique_constraint UNIQUE (name, parent)
);

CREATE TABLE links(
    email VARCHAR(64),
    type VARCHAR(16),
    code  VARCHAR(256),
    CONSTRAINT unique_constraint UNIQUE (code)
);


-- Add universities from: https://universitairemasters.nl/universiteiten/ --
INSERT INTO universities
    (name)
VALUES
    ("Global"),
    ("Erasmus Universiteit Rotterdam"),
    ("Maastricht University"),
    ("Radboud Universiteit"),
    ("Rijksuniversiteit Groningen"),
    ("Tilburg University"),
    ("Universiteit Leiden"),
    ("Universiteit Utrecht"),
    ("Universiteit van Amsterdam"),
    ("Vrije Universiteit Amsterdam"),
    ("Maastricht School of Management"),
    ("Nyenrode Business Universiteit"),
    ("Nederlandse Defensie Academie"),
    ("Universiteit voor Humanistiek"),
    ("Open Universiteit"),
    ("Protestantse Theologische Universiteit"),
    ("Theologische Universiteit Apeldoorn"),
    ("Theologische Universiteit Kampen"),
    ("Technische Universiteit Delft"),
    ("Technische Universiteit Eindhoven"),
    ("Universiteit Twente"),
    ("Wageningen University & Research");

-- Populate test data --
INSERT INTO users
    (name, email, password)
VALUES
    ('test_user_alpha', 'alpha@example.com', '$2b$12$SGY380.14bqpOtclkPf42eyt2RfIuQsoIEYkK16Qj8w0lZuF2qcDy'), -- the word blue hashed --
    ('test_user_bravo', 'bravo@example.com', '$2b$12$v/vd5XM/WLLpMGXeKfrg0u7zd2AcJwQX7NNwSpZs4MXCZ7kYUlvr6'); -- the word yellow hashed --

INSERT INTO writeups
    (challenge_id, user_id, file_name)
VALUES
    (1, 1, "exampleWriteup");