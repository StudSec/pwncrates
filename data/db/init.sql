-- Initialization file, gets called once on database creation. --

CREATE DATABASE pwncrates;
USE pwncrates;

CREATE TABLE users (
  name VARCHAR(20),
  password VARCHAR(16)
);

INSERT INTO users
  (name, password)
VALUES
  ('test_admin', 'blue'),
  ('test_user', 'yellow');