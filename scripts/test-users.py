import sqlite3
import os
import sys

os.chdir(sys.path[0])

sql_statement = """
INSERT INTO users
    (name, email, password)
VALUES
    ('test_user_alpha', 'alpha@example.com', '$2b$12$SGY380.14bqpOtclkPf42eyt2RfIuQsoIEYkK16Qj8w0lZuF2qcDy'), -- the word blue hashed --
    ('test_user_bravo', 'bravo@example.com', '$2b$12$v/vd5XM/WLLpMGXeKfrg0u7zd2AcJwQX7NNwSpZs4MXCZ7kYUlvr6'); -- the word yellow hashed --
"""

with open('../webapp/database/init.sql', 'r') as f:
    sql_code = f.read()

conn = sqlite3.connect('../data/db/pwncrates.db')
if os.path.getsize("../data/db/pwncrates.db") == 0:
    conn.executescript(sql_code)
conn.execute(sql_statement, ())
conn.commit()
