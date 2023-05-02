-- Initialization file, gets called once on database creation. --

CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name VARCHAR(64),
    password VARCHAR(64),
    university_id INTEGER,
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
    user_id INTEGER
);

CREATE TABLE challenges (
    id INTEGER PRIMARY KEY,
    name VARCHAR(128),
    description VARCHAR(2048),
    points INTEGER,
    category VARCHAR(64),
    difficulty INTEGER,
    subcategory VARCHAR(64),
    flag VARCHAR(128),
    solves INTEGER DEFAULT 0
);

CREATE TABLE writeups(
    id INTEGER PRIMARY KEY,
    challenge_id INTEGER,
    user_id INTEGER,
    file_name VARCHAR(256)
);

-- Populate test data --
INSERT INTO universities
    (name)
VALUES
    ("Vrije Universiteit"),
    ("Radboud");

INSERT INTO users
    (name, password, university_id)
VALUES
    ('test_user_alpha', '$2b$12$SGY380.14bqpOtclkPf42eyt2RfIuQsoIEYkK16Qj8w0lZuF2qcDy', 1), -- the word blue hashed --
    ('test_user_bravo', '$2b$12$v/vd5XM/WLLpMGXeKfrg0u7zd2AcJwQX7NNwSpZs4MXCZ7kYUlvr6', 1); -- the word yellow hashed --

INSERT INTO challenges
    (name, description, points, category, difficulty, subcategory, flag)
VALUES
    ("test_challenge_hard", "A hard PWN challenge", 600, "pwn", 3, "KSLR", "CTF{Hard_Challenge_Pwn}"),
    ("test_challenge_medium", "A medium PWN challenge", 200, "pwn", 2, "KSLR", "CTF{Medium_Challenge_Pwn}"),
    ("test_challenge_easy", "An easy PWN challenge", 50, "pwn", 2, "BoF", "CTF{Easy_Challenge_Pwn"),
    ("test_challenge_easy_web", "An easy WEB challenge", 50, "web", 2, "sql", "CTF{Easy_Challenge_Web");

INSERT INTO writeups
    (challenge_id, user_id, file_name)
VALUES
    (1, 1, "exampleWriteup");