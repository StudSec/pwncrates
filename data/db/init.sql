-- Initialization file, gets called once on database creation. --

CREATE DATABASE pwncrates;
USE pwncrates;

CREATE TABLE users (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(64),
    password VARCHAR(64),
    university_id INT,
    PRIMARY KEY (ID)
);

CREATE TABLE universities (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(128),
    PRIMARY KEY (ID)
);

CREATE TABLE solves (
    id INT NOT NULL AUTO_INCREMENT,
    challenge_id INT,
    solved_time INT,  -- Using unix timestamp over builtin datetime because it feels easier to work with - Aidan
    user_id INT,
    PRIMARY KEY (ID)
);

CREATE TABLE challenges (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(128),
    description VARCHAR(2048),
    points INT,
    category VARCHAR(64),
    difficulty INT,
    subcategory VARCHAR(64),
    flag VARCHAR(128),
    PRIMARY KEY (ID)
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
    (name, description, points, category, difficulty, subcategory, flag)
VALUES
    ("test_challenge_hard", "A hard PWN challenge", 600, "pwn", 3, "KSLR", "CTF{Hard_Challenge_Pwn}"),
    ("test_challenge_medium", "A medium PWN challenge", 200, "pwn", 2, "KSLR", "CTF{Medium_Challenge_Pwn}"),
    ("test_challenge_easy", "An easy PWN challenge", 50, "pwn", 2, "BoF", "CTF{Easy_Challenge_Pwn"),
    ("test_challenge_easy_web", "An easy WEB challenge", 50, "web", 2, "sql", "CTF{Easy_Challenge_Web");
