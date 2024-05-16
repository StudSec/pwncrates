CREATE TABLE IF NOT EXISTS pwncrates (
    name VARCHAR(64),
    version FLOAT
);

UPDATE pwncrates SET version = 1.1;

ALTER TABLE challenges ADD COLUMN docker_name TEXT DEFAULT NULL;
