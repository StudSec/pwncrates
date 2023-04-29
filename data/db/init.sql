-- Initialization file, gets called once on database creation. --

CREATE DATABASE pwncrates;
USE pwncrates;

CREATE TABLE users (
    name VARCHAR(64),
    password VARCHAR(64),
    university_id INT
);

CREATE TABLE universities (
    name VARCHAR(128)
);

CREATE TABLE solves (
  challenge_id INT,
  solved_time TIMESTAMP,
  user_id INT
);

CREATE TABLE challenges (
    name VARCHAR(128),
    points INT,
    category VARCHAR(64),
    difficulty INT,
    subcategory VARCHAR(64)
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
    ('test_admin', 'blue', 1),
    ('test_user', 'yellow', 1);

INSERT INTO challenges
    (name, points, category, difficulty, subcategory)
VALUES
    ("test_challenge_hard", 600, "pwn", 3, "KSLR"),
    ("test_challenge_medium", 200, "pwn", 2, "KSLR"),
    ("test_challenge_easy", 50, "pwn", 2, "BoF"),
    ("test_challenge_easy_web", 50, "web", 2, "BoF");
