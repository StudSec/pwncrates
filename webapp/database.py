"""
This file serves as the primary interface between the database and the rest of the code.

Sticking to this convention allows us to easily modify or switch the database without performing shotgun surgery.
"""
from webapp.helpers import *
import cmarkgfm
import sqlite3
import time
import os

import sys


def get_users():
    cursor = conn.execute('SELECT name FROM users')
    results = [name for name in cursor.fetchall()]
    cursor.close()

    return results


def get_username(user_id) -> str:
    cursor = conn.execute('SELECT name FROM users WHERE id = ? LIMIT 1', (user_id,))
    results = [user_id[0] for user_id in cursor.fetchall()]
    cursor.close()

    if len(results) == 0:
        return ""

    return results[0]


def get_university(user_id):
    cursor = conn.execute('SELECT U.name FROM universities U, users A WHERE A.id = ? AND A.university_id = U.id LIMIT 1', (user_id,))
    results = [user_id[0] for user_id in cursor.fetchall()]
    cursor.close()

    if len(results) == 0:
        return ""

    return results[0]


def get_password(user_name) -> str:
    cursor = conn.execute('SELECT password FROM users WHERE name = ? LIMIT 1', (user_name,))
    results = [password_hash[0] for password_hash in cursor.fetchall()]
    cursor.close()

    if len(results) == 0:
        return ""

    return results[0]


def get_id(user_name) -> str:
    cursor = conn.execute('SELECT id FROM users WHERE name = ? LIMIT 1', (user_name,))
    results = [password_hash[0] for password_hash in cursor.fetchall()]
    cursor.close()

    if len(results) == 0:
        return ""

    return results[0]


def register_user(user_name, password, email):
    cursor = conn.execute('INSERT INTO users (name, password, email) VALUES (?, ?, ?)', (user_name, password, email))
    conn.commit()
    cursor.close()
    return


def get_user_information(user_id):
    cursor = conn.execute('SELECT U.name FROM universities U, users A WHERE A.id = ? AND A.university_id = U.id LIMIT 1', (user_id,))
    results = [user_id[0] for user_id in cursor.fetchall()]
    cursor.close()

    if len(results) == 0:
        return ""

    return results[0]
    pass


def get_challenges(category, difficulty="hard"):
    difficulties = {
        "easy": 1,
        "medium": 2,
        "hard": 3
    }
    # Translate the difficulty to int
    difficulty = difficulties[difficulty.lower()]

    cursor = conn.execute('SELECT id, name, description, points, subcategory, url, solves FROM challenges '
                          'WHERE category = ? AND difficulty <= ?',
                          (category, difficulty))
    results = {}
    for (user_id, name, description, points, subcategory, url, solves) in cursor.fetchall():
        handout_file = get_handout_name(category, name)
        if subcategory in results.keys():
            results[subcategory].append((
                user_id, name, cmarkgfm.github_flavored_markdown_to_html(description), points, url, solves,
                handout_file if os.path.exists("static/handouts/" + handout_file) else ""
            ))
        else:
            results[subcategory] = [(
                user_id, name, cmarkgfm.github_flavored_markdown_to_html(description), points, url, solves,
                handout_file if os.path.exists("static/handouts/" + handout_file) else ""
            )]
    cursor.close()

    return results


def get_categories():
    ret = {}

    cursor = conn.execute('SELECT DISTINCT category FROM challenges;')
    results = [category[0] for category in cursor.fetchall()]
    cursor.close()

    cursor = conn.cursor()
    for category in results:
        cursor.execute('SELECT description FROM categories WHERE name = ? AND parent = ? LIMIT 1;', (category, category))
        description = cursor.fetchone()
        if description:
            ret[category] = cmarkgfm.github_flavored_markdown_to_html(description[0])
        else:
            ret[category] = ""
    cursor.close()

    return ret


def submit_flag(challenge_id, flag, user_id):
    cursor = conn.execute('SELECT DISTINCT flag FROM challenges WHERE id = ? AND flag = ?;', (challenge_id, flag))

    if cursor.fetchone():
        cursor = conn.execute('SELECT id FROM solves WHERE challenge_id = ? AND user_id = ?;', (challenge_id, user_id))
        if cursor.fetchone():
            ret = "Already solved"
        else:
            conn.execute('INSERT INTO solves (challenge_id, solved_time, user_id) VALUES (?, ?, ?);',
                         (challenge_id, int(time.time()), user_id))
            conn.execute('UPDATE challenges SET solves = solves + 1 WHERE id = ?', (challenge_id,))
            conn.execute('UPDATE users SET points = points + '
                         '(SELECT points FROM challenges WHERE id = ?) '
                         'WHERE id = ?', (challenge_id, user_id))
            conn.commit()
            ret = "OK"
    else:
        ret = "Incorrect flag"

    cursor.close()

    return ret


def get_scoreboard():
    cursor = conn.execute('SELECT name, points FROM users ORDER BY points DESC;')
    results = [user for user in cursor.fetchall()]
    cursor.close()

    return results


def get_solves(user_id):
    cursor = conn.execute('SELECT challenge_id FROM solves WHERE user_id = ?;', (user_id,))
    results = [challenge_id[0] for challenge_id in cursor.fetchall()]
    cursor.close()

    return results


def get_writeups(challenge_id):
    cursor = conn.execute('SELECT U.name, W.id FROM writeups AS W, users AS U '
                          'WHERE W.challenge_id = ? AND W.user_id = U.id;', (challenge_id,))
    results = [(name, writeup_id) for name, writeup_id in cursor.fetchall()]
    cursor.close()

    return results


def get_writeup_file(challenge_id, writeup_id):
    cursor = conn.execute('SELECT file_name FROM writeups '
                          'WHERE challenge_id = ? AND id = ?;', (challenge_id, writeup_id))
    results = [filename[0] for filename in cursor.fetchall()]
    cursor.close()

    return results


def get_challenge_name(challenge_id):
    cursor = conn.execute('SELECT name FROM challenges '
                          'WHERE id = ?;', (challenge_id,))
    results = [filename[0] for filename in cursor.fetchall()]
    cursor.close()

    return results


def initialize_database():
    with open('init.sql', 'r') as f:
        sql_code = f.read()
    conn.executescript(sql_code)
    conn.commit()


def update_or_create_challenge(path):
    # Get information
    category, name, _ = path.split("/", 2)

    # Specify path to start in git directory
    challenge_data = parse_markdown_challenge("challenges/Challenges/" + path)

    if challenge_data == {}:
        return

    difficulties = {
        "easy": 1,
        "medium": 2,
        "hard": 3
    }

    difficulty = difficulties[challenge_data["difficulty"].lower()]

    cursor = conn.execute('INSERT OR REPLACE INTO challenges '
                          '(name, description, points, category, difficulty, subcategory, flag, url) '
                          'values (?, ?, ?, ?, ?, ?, ?, ?);'
                          , (name, challenge_data["description"], challenge_data["points"], category,
                             difficulty, challenge_data["subcategory"], challenge_data["flag"], challenge_data["url"]))
    conn.commit()
    cursor.close()


def update_or_create_category(path):
    categories, parent = parse_markdown_category(path)

    cursor = conn.cursor()
    for category in categories:
        cursor.execute('INSERT OR REPLACE INTO categories (name, description, parent) values (?, ?, ?);',
                       (category, categories[category], parent))
    conn.commit()
    cursor.close()


# Is this unsafe with regards to multithreading?
conn = sqlite3.connect('./db/pwncrates.db', check_same_thread=False)
if os.path.getsize("./db/pwncrates.db") == 0:
    initialize_database()

