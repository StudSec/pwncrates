"""
This file serves as the primary interface between the database and the rest of the code.

Sticking to this convention allows us to easily modify or switch the database without performing shotgun surgery.
"""
from datetime import datetime
from webapp.helpers import *
from webapp import app
import cmarkgfm
import sqlite3
import time
import os


# Lookup functions
def get_email_from_link(link_type, code):
    assert link_type == "confirmation" or link_type == "reset"

    cursor = conn.execute("SELECT email FROM links WHERE code = ? AND type = ?", (code, link_type))

    results = [email[0] for email in cursor.fetchall()]
    cursor.close()
    return results


def get_link_from_email(email, link_type):
    assert link_type == "confirmation" or link_type == "reset"

    cursor = conn.execute("SELECT code FROM links WHERE email = ? AND type = ?", (email, link_type))

    results = [code[0] for code in cursor.fetchall()]
    cursor.close()

    return results


def get_challenges(category, difficulty="hard"):
    difficulties = {
        "easy": 1,
        "medium": 2,
        "hard": 3
    }
    # Translate the difficulty to int
    difficulty = difficulties[difficulty.lower()]

    cursor = conn.execute('SELECT B.description, A.id, A.name, A.description, A.points, A.subcategory, A.url, '
                          '(SELECT COUNT(*) FROM solves S WHERE S.challenge_id = A.id) AS solve_count, '
                          'A.docker_name, A.difficulty '
                          'FROM challenges A '
                          'LEFT JOIN categories B ON A.subcategory = B.name AND B.parent = A.category '
                          'WHERE A.category = ? AND A.difficulty <= ? '
                          'ORDER BY A.points ASC',
                          (category, difficulty))

    results = {}

    for (category_description, user_id, name, description, points, subcategory, url, solves, docker_name,
         difficulty) in cursor.fetchall():
        handout_file = get_handout_name(category, name)

        if not subcategory:
            subcategory = ""

        if not category_description:
            category_description = ""

        challenge_info = (
            user_id, name, cmarkgfm.github_flavored_markdown_to_html(description), points, url, solves, docker_name,
            handout_file if os.path.exists("static/handouts/" + handout_file) else "",
            list(difficulties.keys())[difficulty - 1]
        )

        if subcategory in results.keys():
            results[subcategory][1].append(challenge_info)
        else:
            results[subcategory] = (cmarkgfm.github_flavored_markdown_to_html(category_description), [challenge_info])

    cursor.close()

    ret = []
    for i in results:
        ret.append((i, results[i][0], results[i][1]))

    return ret


def get_user_solves(user_id):
    cursor = conn.execute('SELECT S.challenge_id, C.name, S.solved_time, C.points FROM solves S, Challenges C WHERE '
                          'S.user_id = ? AND C.id = S.challenge_id ORDER BY S.solved_time DESC;', (user_id,))
    results = [(solve_data[0], solve_data[1], datetime.utcfromtimestamp(solve_data[2]).strftime('%Y-%m-%d %H:%M:%S'),
                solve_data[3])
               for solve_data in cursor.fetchall()]
    cursor.close()
    return results


def get_user_scores(user_id):
    cursor = conn.execute('SELECT S.challenge_id, C.name, S.solved_time, C.points FROM solves S, Challenges C WHERE '
                          'S.user_id = ? AND C.id = S.challenge_id ORDER BY S.solved_time DESC;', (user_id,))
    score = 0
    results = []
    solves = cursor.fetchall()
    solves.reverse()
    for solve_data in solves:
        # Chart js for some god forsaken reason is using miliseconds for their timestamp
        score += int(solve_data[3])
        results.append([solve_data[2] * 1000, score])
    cursor.close()
    return results


def get_challenge_solves(challenge_id):
    cursor = conn.execute('SELECT U.name, S.solved_time FROM solves S, users U  '
                          'WHERE S.challenge_id = ? AND S.user_id = U.id ORDER BY S.solved_time DESC;', (challenge_id,))
    results = [(solve[0], datetime.utcfromtimestamp(solve[1]).strftime('%Y-%m-%d %H:%M:%S'))
               for solve in cursor.fetchall()]
    cursor.close()

    return results


def get_scoreboard():
    cursor = conn.execute('SELECT U.id, U.name, U.university_id, A.name, IFNULL(SUM(C.points), 0) AS total_points,  '
                          'MAX(S.solved_time) AS latest_solve_time '
                          'FROM universities A, users U LEFT JOIN solves S ON U.id = S.user_id '
                          'LEFT JOIN challenges C ON S.challenge_id = C.id WHERE A.id = U.university_id'
                          ' GROUP BY U.id ORDER BY total_points DESC, latest_solve_time ASC;')
    results = [user for user in cursor.fetchall()]
    cursor.close()

    return results


def get_users():
    cursor = conn.execute('SELECT name FROM users')
    results = [name[0] for name in cursor.fetchall()]
    cursor.close()

    return results


def get_universities():
    cursor = conn.execute('SELECT id, name FROM universities')
    results = [university_id for university_id in cursor.fetchall()]
    cursor.close()

    return results


def get_scoreboard_universities():
    cursor = conn.execute(
        'SELECT distinct A.id, A.name FROM users U left join universities A on U.university_id = A.id')
    results = [university_id for university_id in cursor.fetchall()]
    cursor.close()
    return results


def get_categories():
    ret = {}

    cursor = conn.execute('SELECT DISTINCT category FROM challenges;')
    results = [category[0] for category in cursor.fetchall()]
    cursor.close()

    cursor = conn.cursor()
    for category in results:
        cursor.execute('SELECT description FROM categories WHERE name = ? AND parent = ? LIMIT 1;',
                       (category, category))
        description = cursor.fetchone()
        if description:
            ret[category] = cmarkgfm.github_flavored_markdown_to_html(description[0])
        else:
            ret[category] = ""
    cursor.close()

    return ret


def get_writeups(challenge_id):
    cursor = conn.execute('SELECT U.name, U.id FROM writeups AS W, users AS U '
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
    results = cursor.fetchone()[0]
    cursor.close()

    return results


def get_challenge_id(challenge_name):
    cursor = conn.execute('SELECT id FROM challenges WHERE name = ?', (challenge_name,))
    challenge_id = cursor.fetchone()[0]
    cursor.close()

    return challenge_id


def get_writeup_file(challenge_id, user_id):
    cursor = conn.execute('SELECT file_name FROM writeups WHERE challenge_id = ? AND user_id = ?;',
                          (challenge_id, user_id))

    ret = cursor.fetchone()
    cursor.close()

    if ret and len(ret) != 0:
        return ret[0]
    else:
        return None


# User functions
def get_user(user_id=None, email=None):
    if user_id:
        cursor = conn.execute(
            'SELECT U.email, U.name, U.university_id, A.name, U.discord_id, U.password '
            'FROM users U LEFT JOIN universities A ON U.university_id = A.id '
            'WHERE U.id = ? LIMIT 1;', (user_id,))
        results = [
            {
                "id": user_id,
                "email": user_info[0],
                "username": user_info[1],
                "university_id": user_info[2],
                "university_name": user_info[3],
                "discord_id": user_info[4],
                "password": user_info[5],
            } for user_info in cursor.fetchall()
        ]
        cursor.close()

        if len(results) == 0:
            return ""

        return results[0]
    if email:
        cursor = conn.execute(
            'SELECT U.id, U.name, U.university_id, A.name, U.discord_id, U.password '
            'FROM users U LEFT JOIN universities A ON U.university_id = A.id '
            'WHERE U.email = ? LIMIT 1;', (email,))
        results = [
            {
                "id": user_info[0],
                "email": email,
                "username": user_info[1],
                "university_id": user_info[2],
                "university_name": user_info[3],
                "discord_id": user_info[4],
                "password": user_info[5],
            } for user_info in cursor.fetchall()
        ]
        cursor.close()

        if len(results) == 0:
            return ""

        return results[0]
    return ""


def get_user_information(user_id):
    cursor = conn.execute(
        'SELECT U.name FROM universities U, users A WHERE A.id = ? AND A.university_id = U.id LIMIT 1', (user_id,))
    results = [user_id[0] for user_id in cursor.fetchall()]
    cursor.close()

    if len(results) == 0:
        return ""

    return results[0]


def get_email_from_discord_id(discord_id):
    cursor = conn.execute('SELECT email FROM users WHERE discord_id = ? LIMIT 1', (discord_id,))
    results = [user_info for user_info in cursor.fetchall()]
    cursor.close()

    if len(results) == 0:
        return ""

    return results[0]


def get_docker_service_name(challenge_id):
    cursor = conn.execute('SELECT docker_name FROM challenges WHERE id=? LIMIT 1', (challenge_id,))
    result = cursor.fetchone()
    if result is None:
        return None
    else:
        return result[0]


# Actions
def register_user(user_name, password, email):
    cursor = conn.execute('INSERT INTO users (name, password, email) VALUES (?, ?, ?)',
                          (user_name, password, email))
    conn.commit()
    cursor.close()
    return


def change_user_password(email, password):
    cursor = conn.execute('UPDATE users SET password = ? WHERE email = ?', (password, email))
    conn.commit()
    cursor.close()
    return


def create_or_update_writeup(challenge_id, user_id, file_name):
    cursor = conn.execute('INSERT OR IGNORE INTO writeups (challenge_id, user_id, file_name) VALUES (?, ?, ?);',
                          (challenge_id, user_id, file_name))
    cursor = cursor.execute('UPDATE writeups SET file_name = ? WHERE challenge_id = ? AND user_id = ?;',
                            (file_name, challenge_id, user_id))
    conn.commit()
    cursor.close()
    return


def remove_writeup(challenge_id, user_id):
    cursor = conn.execute('DELETE FROM writeups WHERE challenge_id = ? AND user_id = ?',
                          (challenge_id, user_id))
    conn.commit()
    cursor.close()
    return


def submit_flag(challenge_id, flag, user_id):
    cursor = conn.execute('SELECT DISTINCT flag FROM challenges WHERE id = ? AND ((flag = ?) OR '
                          '(flag_case_insensitive = 1 AND lower(flag) = ?)) ;',
                          (challenge_id, flag, flag.lower()))

    if cursor.fetchone():
        cursor = conn.execute('SELECT id FROM solves WHERE challenge_id = ? AND user_id = ?;',
                              (challenge_id, user_id))
        if cursor.fetchone():
            ret = "Already solved"
        else:
            conn.execute('INSERT INTO solves (challenge_id, solved_time, user_id) VALUES (?, ?, ?);',
                         (challenge_id, int(time.time()), user_id))
            conn.commit()
            ret = "OK"
    else:
        ret = "Incorrect flag"

    cursor.close()

    return ret


def update_discord_id(discord_id, email):
    conn.execute("UPDATE users SET discord_id = ? WHERE email = ?", (discord_id, email))
    conn.commit()
    return


def update_user_university(user_id, university_id):
    conn.execute("UPDATE users SET university_id = ? WHERE id = ?", (university_id, user_id))
    conn.commit()
    return


def initialize_database():
    with open('database/init.sql', 'r') as f:
        sql_code = f.read()

    conn.executescript(sql_code)
    conn.commit()


def update_database():
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pwncrates'")
    result = cursor.fetchone()
    if not result:
        database_version = "0.0"
    else:
        cursor.execute("SELECT version FROM pwncrates")
        database_version = str(cursor.fetchone()[0])

    files = [x for x in os.listdir("database/") if x.startswith("migration") and
             str(x.split("-")[1]) == database_version]

    while len(files) != 0:
        with open(f"database/{files[0]}") as f:
            conn.executescript(f.read())
        conn.commit()
        cursor.execute("SELECT version FROM pwncrates")
        database_version = str(cursor.fetchone()[0])
        assert (database_version == str(files[0].split("-")[2].split(".sql")[0]))
        files = [x for x in os.listdir("database/") if
                 x.startswith("migration") and str(x.split("-")[1]) == database_version]

    cursor.close()


def update_or_create_challenge(path, folder=get_challenge_path()):
    # Get information
    category, name, _ = path.split("/", 2)

    # Specify path to start in git directory
    challenge_data = parse_markdown_challenge(folder + path)

    if challenge_data == {}:
        return

    difficulties = {
        "easy": 1,
        "medium": 2,
        "hard": 3
    }

    difficulty = difficulties[challenge_data["difficulty"].lower()]
    cursor = conn.cursor()

    cursor.execute('INSERT OR IGNORE INTO challenges '
                   '(name, description, points, category, difficulty, subcategory, flag, flag_case_insensitive, url, docker_name) '
                   'values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'
                   , (name, challenge_data["description"], challenge_data["points"], category,
                      difficulty, challenge_data["subcategory"], challenge_data["flag"],
                      bool(challenge_data["case_insensitive"]), challenge_data["url"], challenge_data["docker_name"]
                      ))

    cursor.execute('UPDATE challenges SET description = ?, points = ?, category = ?, difficulty = ?, '
                   'subcategory = ?, flag = ?, flag_case_insensitive = ?, url = ?, docker_name = ? WHERE name = ?',
                   (challenge_data["description"], challenge_data["points"], category, difficulty,
                    challenge_data["subcategory"], challenge_data["flag"], bool(challenge_data["case_insensitive"]),
                    challenge_data["url"], challenge_data["docker_name"], name))

    conn.commit()

    cursor.execute('SELECT id FROM challenges WHERE name = ?', (name,))
    challenge_id = cursor.fetchone()[0]

    cursor.close()
    return challenge_id


def update_or_create_category(path, folder=get_challenge_path()):
    categories, parent = parse_markdown_category(folder + path)

    cursor = conn.cursor()
    for category in categories:
        cursor.execute('INSERT OR IGNORE INTO categories (name, description, parent) values (?, ?, ?);',
                       (category, categories[category], parent))
        cursor.execute('UPDATE categories SET description = ? WHERE name = ? AND parent = ?',
                       (categories[category], category, parent))

    conn.commit()
    cursor.close()


def insert_link(email, link_type, code):
    assert (link_type == "confirmation" or link_type == "reset")

    cursor = conn.cursor()
    cursor.execute("INSERT INTO links (email, type, code) VALUES (?, ?, ?);", (email, link_type, code))
    conn.commit()


def remove_link(link_type, code):
    assert (link_type == "confirmation" or link_type == "reset")

    cursor = conn.cursor()
    cursor.execute("DELETE FROM links WHERE type = ? AND code = ?;", (link_type, code))
    conn.commit()

    if cursor.rowcount > 0:
        return cursor.rowcount
    else:
        return ""


os.system("mkdir /webapp/db")
os.system("touch /webapp/db/pwncrates.db")

if app.debug:
    app.logger.warning("App is running in debug mode, SQLite3 thread checks turned off")
    conn = sqlite3.connect('./db/pwncrates.db', check_same_thread=False)
else:
    # This *should* not cause any conflict, each worker has its own connection. The only conflict is when the git thread
    # attempts changes. Which happens in a separate thread.
    conn = sqlite3.connect('./db/pwncrates.db', check_same_thread=False)

try:
    if os.path.getsize("./db/pwncrates.db") == 0:
        initialize_database()
    update_database()
except sqlite3.OperationalError:
    # Here we assume a different worker beat us to it, though we should find a better solution.
    pass
