import sqlite3
import secrets
import random
import bcrypt
import csv
import os
import sys

os.chdir(sys.path[0])

nato = [
    "Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot", "Golf", "Hotel", "India",
    "Juliett", "Kilo", "Lima", "Mike", "November", "Oscar", "Papa", "Quebec", "Romeo",
    "Sierra", "Tango", "Uniform", "Victor", "Whiskey", "X-ray", "Yankee", "Zulu"
]
with open("words.txt", "r") as f:
    words = f.read().replace("'", "").splitlines()


def register_user(user_name, password, email):
    cursor = conn.execute('INSERT INTO users (name, password, email) VALUES (?, ?, ?)',
                          (user_name, password, email))
    conn.commit()
    cursor.close()
    return


with open('../webapp/database/init.sql', 'r') as f:
    sql_code = f.read()

conn = sqlite3.connect('../data/db/pwncrates.db')
if os.path.getsize("../data/db/pwncrates.db") == 0:
    conn.executescript(sql_code)

with open('users.csv') as csvfile:
    users = csv.reader(csvfile, delimiter=',')
    for user in users:
        username = user[0]
        password = user[2]
        email = user[1]

        if not username:
            username = "-".join([random.choice(list(nato)) for _ in range(3)])
        if not password:
            password = "".join([secrets.choice(words) for _ in range(4)]).lower()
        if not email:
            email = "".join([random.choice(words) for _ in range(1)])
            email += "".join([str(random.randint(0, 9)) for _ in range(4)])
            email += "@example.com"
        print("Adding:", username, password, email)
        try:
            register_user(username, bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('ascii'), email)
        except sqlite3.IntegrityError:
            pass

conn.commit()
