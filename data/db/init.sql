-- Initialization file, gets called once on database creation. --

CREATE DATABASE pwncrates;
USE pwncrates;

CREATE TABLE users (
    name VARCHAR(32),
    password VARCHAR(16)
);

CREATE TABLE challenges (
    name VARCHAR(128),
    points INT,
    category VARCHAR(64),
    difficulty INT,
    subcategory VARCHAR(64)
);

-- Populate test data --
INSERT INTO users
    (name, password)
VALUES
    ('test_admin', 'blue'),
    ('test_user', 'yellow');

INSERT INTO challenges
    (name, points, category, difficulty, subcategory)
VALUES
    ("test_challenge_hard", 600, "pwn", 3, "KSLR"),
    ("test_challenge_medium", 200, "pwn", 2, "KSLR"),
    ("test_challenge_easy", 50, "pwn", 2, "BoF"),
    ("test_challenge_easy_web", 50, "web", 2, "BoF");
