CREATE TABLE IF NOT EXISTS pwncrates (
    name VARCHAR(64),
    version FLOAT
);

INSERT INTO pwncrates (name, version) VALUES ('pwncrates', 1.0);

ALTER TABLE challenges ADD COLUMN flag_case_insensitive BOOLEAN DEFAULT FALSE;
