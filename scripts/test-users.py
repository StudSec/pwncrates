import sqlite3

sql_statement = """
INSERT INTO users
    (name, email, password)
VALUES
    ('test_user_alpha', 'alpha@example.com', '$2b$12$SGY380.14bqpOtclkPf42eyt2RfIuQsoIEYkK16Qj8w0lZuF2qcDy'), -- the word blue hashed --
    ('test_user_bravo', 'bravo@example.com', '$2b$12$v/vd5XM/WLLpMGXeKfrg0u7zd2AcJwQX7NNwSpZs4MXCZ7kYUlvr6'); -- the word yellow hashed --
"""

with open('webapp/init.sql', 'r') as f:
    sql_code = f.read()

conn = sqlite3.connect('data/db/pwncrates.db')
conn.executescript(sql_code)
conn.execute(sql_statement, ())
conn.commit()
