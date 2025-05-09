"""
This file serves as the primary interface between the database and the rest of the code.

Sticking to this convention allows us to easily modify or switch the database without performing shotgun surgery.
"""
from datetime import datetime, timezone
from pwncrates.helpers import *
from pwncrates.time_window import get_scoreboard_freeze_time
from pwncrates import app
import cmarkgfm
import sqlite3
import time
import os


# Admin functions
def promote_user(user_id):
    try:
        cursor = conn.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (user_id,))
        conn.commit()
        cursor.close()
        
        # True if updated
        return cursor.rowcount == 1
    except Exception as e:
        # Log the error if necessary
        print(f"Error promoting user {user_id}: {e}")
        return False


def demote_user(user_id):
    try:
        cursor = conn.execute("DELETE FROM admins WHERE user_id = ?", (user_id,))
        conn.commit()  # Commit the transaction
        cursor.close()
        
        # True if updated
        return cursor.rowcount == 1
    except Exception as e:
        # Log the error if necessary
        print(f"Error demoting user {user_id}: {e}")

        return False


def hide_user(user_id):
    try:
        cursor = conn.execute("INSERT OR IGNORE INTO hidden_users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        cursor.close()
        
        # True if updated
        return cursor.rowcount == 1
    except Exception as e:
        # Log the error if necessary
        print(f"Error promoting user {user_id}: {e}")

        return False
    
def show_user(user_id):
    try:
        cursor = conn.execute("DELETE from hidden_users where user_id = ?", (user_id,))
        conn.commit()
        cursor.close()
        
        # True if updated
        return cursor.rowcount == 1
    except Exception as e:
        # Log the error if necessary
        print(f"Error promoting user {user_id}: {e}")

        return False

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
    freeze_time = get_scoreboard_freeze_time()

    if freeze_time:
        solve_count_subquery = (
            '(SELECT COUNT(*) FROM solves S WHERE S.challenge_id = A.id AND S.solved_time < ?)'
        )
        params = [category, difficulty, freeze_time]
    else:
        solve_count_subquery = '(SELECT COUNT(*) FROM solves S WHERE S.challenge_id = A.id)'
        params = [category, difficulty]

    query = f'''
            SELECT B.description, A.uuid, A.name, A.description, A.points, B.name, C.url,
                   {solve_count_subquery} AS solve_count,
                   A.difficulty
            FROM challenges A
            LEFT JOIN categories B ON A.category = B.uuid AND B.parent_id NOT NULL
            LEFT JOIN challenge_urls C ON C.challenge_id = A.id
            WHERE A.category = ? AND A.difficulty <= ?
            ORDER BY A.points ASC
        '''

    cursor = conn.execute(query, params)

    results = {}

    for (category_description, challenge_uuid, name, description, points, subcategory, url, solves, difficulty) \
            in cursor.fetchall():
        handout_file = get_handout_name(challenge_uuid)

        if not subcategory:
            subcategory = ""

        if not category_description:
            category_description = ""

        challenge_info = (
            challenge_uuid, name, cmarkgfm.github_flavored_markdown_to_html(description), points, url, solves,
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
    freeze_time = get_scoreboard_freeze_time()
    query = (
        'SELECT C.uuid, C.name, S.solved_time, C.points '
        'FROM solves S, Challenges C '
        'WHERE S.user_id = ? AND C.id = S.challenge_id'
    )
    params = [user_id]

    if freeze_time:
        query += ' AND S.solved_time < ?'
        params.append(freeze_time)

    query += ' ORDER BY S.solved_time DESC;'
    cursor = conn.execute(query, params)

    results = [
        (
            uuid,
            name,
            datetime.fromtimestamp(solved_time, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
            points
        )
        for uuid, name, solved_time, points in cursor.fetchall()
    ]

    cursor.close()
    return results



def get_user_scores(user_id):
    freeze_time = get_scoreboard_freeze_time()
    query = (
        'SELECT S.solved_time, C.points FROM solves S, Challenges C '
        'WHERE S.user_id = ? AND C.id = S.challenge_id'
    )
    params = [user_id]

    if freeze_time:
        query += ' AND S.solved_time < ?'
        params.append(freeze_time)

    query += ' ORDER BY S.solved_time DESC;'

    cursor = conn.execute(query, params)
    solves = cursor.fetchall()
    cursor.close()

    score = 0
    results = []
    for solved_time, points in reversed(solves):
        score += int(points)
        results.append([solved_time * 1000, score])  # Chart.js expects milliseconds

    return results


def get_challenge_solves(challenge_id):
    freeze_time = get_scoreboard_freeze_time()
    query = (
        'SELECT U.name, S.solved_time FROM solves S, users U, challenges C '
        'WHERE S.challenge_id = C.id AND C.uuid = ? AND S.user_id = U.id'
    )
    params = [challenge_id]

    if freeze_time:
        query += ' AND S.solved_time < ?'
        params.append(freeze_time)

    query += ' ORDER BY S.solved_time DESC;'

    cursor = conn.execute(query, params)
    results = [
        (username, datetime.fromtimestamp(solved_time, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S'))
        for username, solved_time in cursor.fetchall()
    ]
    cursor.close()

    return results



def get_scoreboard():
    freeze_time = get_scoreboard_freeze_time()

    # Conditional filter for freeze time in LEFT JOIN
    time_condition = "AND S.solved_time < ?" if freeze_time else ""
    params = (freeze_time,) if freeze_time else ()

    query = f'''
        SELECT 
            U.id, 
            U.name, 
            U.university_id, 
            A.name, 
            IFNULL(SUM(C.points), 0) AS total_points,
            MAX(S.solved_time) AS latest_solve_time
        FROM universities A, users U 
        LEFT JOIN solves S ON U.id = S.user_id {time_condition}
        LEFT JOIN challenges C ON S.challenge_id = C.id 
        WHERE A.id = U.university_id
        AND U.id NOT IN (SELECT user_id FROM hidden_users)
        GROUP BY U.id 
        ORDER BY total_points DESC, latest_solve_time ASC;
    '''

    cursor = conn.execute(query, params)
    results = [user for user in cursor.fetchall()]
    cursor.close()

    return results



def get_users():
    cursor = conn.execute('''
        SELECT 
            U.id, 
            U.name, 
            U.university_id, 
            A.name AS university_name, 
            CASE 
                WHEN AD.user_id IS NOT NULL THEN 1 
                ELSE 0 
            END AS is_admin,
            CASE 
                WHEN H.user_id IS NOT NULL THEN 1 
                ELSE 0 
            END AS is_hidden
        FROM 
            universities A 
            JOIN users U ON A.id = U.university_id
            LEFT JOIN admins AD ON U.id = AD.user_id
            LEFT JOIN hidden_users H ON U.id = H.user_id
    ''')
    
    results = [{
        'user_id': user[0],
        'name': user[1],
        'university_id': user[2],
        'university_name': user[3],
        'is_admin': bool(user[4]),
        'is_hidden': bool(user[5])
    } for user in cursor.fetchall()]
    
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

    cursor = conn.execute('SELECT DISTINCT uuid, name, description FROM categories WHERE parent_id IS NULL;')
    results = [category for category in cursor.fetchall()]
    cursor.close()

    cursor = conn.cursor()
    for category in results:
        if category[2]:
            ret[str(category[0])] = (category[1], cmarkgfm.github_flavored_markdown_to_html(category[2]))
        else:
            ret[str(category[0])] = (category[1], "")
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
                          'WHERE uuid = ?;', (challenge_id,))
    results = cursor.fetchone()[0]
    cursor.close()

    return results


def get_challenge_id(challenge_name):
    cursor = conn.execute('SELECT id FROM challenges WHERE name = ?', (challenge_name,))
    challenge_id = cursor.fetchone()[0]
    cursor.close()

    return challenge_id


def is_user_admin(user_id):
    cursor = conn.execute(
        'SELECT user_id FROM admins WHERE user_id = ? LIMIT 1', (user_id,))
    results = cursor.fetchall()
    cursor.close()

    if len(results) == 0:
        return False  # User is not an admin

    return True  # User is an admin


# User functions
def get_user(user_id=None, email=None, discord_id=None):
    if not any([user_id, email, discord_id]):
        return ""

    query = (
        "SELECT U.id, U.email, U.name, U.university_id, A.name, U.discord_id, U.password "
        "FROM users U LEFT JOIN universities A ON U.university_id = A.id "
    )

    params = []
    if user_id:
        query += "WHERE U.id = ? "
        params.append(user_id)
    if email:
        query += "WHERE U.email = ? "
        params.append(email)
    if discord_id:
        query += "WHERE U.discord_id = ?"
        params.append(discord_id)
    query += "LIMIT 1;"
    
    cursor = conn.execute(query, params)
    user_info = cursor.fetchone()
    cursor.close()

    if not user_info:
        return {}

    return {
        "id": user_info[0],
        "email": user_info[1],
        "username": user_info[2],
        "university_id": user_info[3],
        "university_name": user_info[4],
        "discord_id": user_info[5],
        "password": user_info[6],
        "admin": is_user_admin(user_info[0])
    }


# NOTE: this is now broken, needs to be refactored
def get_docker_service_name(challenge_id):
    cursor = conn.execute('SELECT docker_name FROM challenges WHERE id=? LIMIT 1', (challenge_id,))
    result = cursor.fetchone()
    if result is None:
        return None
    else:
        return result[0]


# Actions
def update_or_create_user(user_id, user_data=None):
    params = []

    if not user_id and all([
        user_data.get("username", None),
        user_data.get("password", None),
        user_data.get("email", None)
    ]):
        cursor = conn.execute('INSERT INTO users (name, password, email) VALUES (?, ?, ?)',
                              (user_data["username"], user_data["password"], user_data["email"]))
        conn.commit()
        cursor.close()
        user_id = get_user(email=user_data["email"])["id"]

    elif user_data.get("password", None):
        params.append(("password = ? ", user_data["password"]))

    if user_data.get("discord_id", None):
        params.append(("discord_id = ? ", user_data["discord_id"]))

    if user_data.get("university_id", None):
        params.append(("university_id = ? ", user_data["university_id"]))

    if params:
        cursor = conn.execute("UPDATE users SET " + ",".join([str(x[0]) for x in params]) + "WHERE id = ?",
                              [x[1] for x in params] + [user_id])
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


def submit_flag(challenge_uuid, flag, user_id):
    challenge_id = conn.execute('SELECT id FROM challenges WHERE uuid = ?', (challenge_uuid,)).fetchone()

    if not challenge_id:
        return "Challenge not found"

    challenge_id = challenge_id[0]

    cursor = conn.execute('SELECT flag FROM challenge_flags WHERE challenge_id = ? AND flag = ?;',
                          (challenge_id, flag))

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


def initialize_database():
    with open('database/init.sql', 'r') as f:
        sql_code = f.read()

    conn.executescript(sql_code)
    conn.commit()


def update_database():
    app.logger.info("running update function")
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pwncrates'")
        result = cursor.fetchone()
        if not result:
            database_version = "0.0"
        else:
            cursor.execute("SELECT version FROM pwncrates")
            database_version = str(cursor.fetchone()[0])

        app.logger.info(f"Database version: {database_version}")

        files = [x for x in os.listdir("database/") if x.startswith("migration") and
                 str(x.split("-")[1]) == database_version]

        while len(files) != 0:
            app.logger.info(f"Running update script {files[0]}")

            with open(f"database/{files[0]}") as f:
                script = f.read()

            try:
                conn.execute("BEGIN")
                for stmt in script.split(';'):
                    stmt = stmt.strip()
                    if stmt:
                        try:
                            cursor.execute(stmt)
                        except sqlite3.OperationalError as e:
                            app.logger.error(f"SQLite error: {e} while executing:\n{stmt}")
                            raise  # Re-raise to trigger rollback

                cursor.execute("SELECT version FROM pwncrates")
                database_version = str(cursor.fetchone()[0])
                expected_version = str(files[0].split("-")[2].split(".sql")[0])
                assert database_version == expected_version

                conn.commit()
            except Exception as e:
                conn.rollback()
                app.logger.error(f"Migration failed for {files[0]}: {e}")
                raise

            files = [x for x in os.listdir("database/") if
                     x.startswith("migration") and str(x.split("-")[1]) == database_version]

    finally:
        cursor.close()


def update_or_create_challenge(challenge, legacy=False):
    difficulties = {
        "easy": 1,
        "medium": 2,
        "hard": 3
    }

    cursor = conn.cursor()

    # Check if a challenge exists with the same name but with an incorrect uuid, if so set it
    if legacy:
        # See if there is a challenge without uuid and same name
        cursor.execute('SELECT id FROM challenges WHERE uuid IS NULL and name = ?', (challenge.name,))
        challenge_id = cursor.fetchone()
        if challenge_id:
            cursor.execute('UPDATE challenges SET uuid = ? WHERE id = ?', (challenge.uuid, challenge_id))

    try:
        # Convert the difficulty string to the numeric value, this allows us to filter.
        difficulty = difficulties[challenge.difficulty.lower()]

        if len(challenge.flag.keys()) > 1:
            app.logger.warning(f"Challenge {challenge.name} has more than 1 flag, this is currently unsupported!")
        flag = list(challenge.flag.keys())[0]
        points = challenge.flag[flag]

        cursor.execute('INSERT OR IGNORE INTO challenges '
                   '(uuid, name, description, category, difficulty, points) '
                   'values (?, ?, ?, ?, ?, ?);'
                   , (challenge.uuid, challenge.name, challenge.description, challenge.category, difficulty, points)
                )

        cursor.execute('UPDATE challenges SET name = ?, description = ?, category = ?, difficulty = ?, points = ? '
                   'WHERE uuid = ?',
                   (challenge.name, challenge.description, challenge.category, difficulty, points, challenge.uuid)
                )

        cursor.execute('SELECT id FROM challenges WHERE uuid = ?', (challenge.uuid,))
        challenge_id = cursor.fetchone()[0]


        cursor.execute('DELETE FROM challenge_urls WHERE challenge_id = ?', (challenge_id,))
        for url in challenge.url:
            cursor.execute('INSERT or IGNORE INTO challenge_urls (challenge_id, url) VALUES (?, ?)',
                           (challenge_id, url))

        cursor.execute('DELETE FROM challenge_flags WHERE challenge_id = ?', (challenge_id,))
        cursor.execute('INSERT or IGNORE into challenge_flags (flag, challenge_id) VALUES (?, ?)', (flag, challenge_id))

        conn.commit()
        app.logger.info(f"Successfully processed challenge: {challenge.name}")

    except AttributeError as e:
        app.logger.error(f"Missing required field in challenge {challenge.name}: {e}")
    except Exception as e:
        app.logger.error(f"Error processing challenge {challenge.name}: {e}")
        import traceback
        traceback.print_exc()

    cursor.close()


def update_or_create_category(category):
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO categories (uuid, name, description, parent_id) values (?, ?, ?, ?);',
                   (category.uuid, category.name, category.description, category.parent))
    cursor.execute('UPDATE categories SET name = ?, description = ?, parent_id = ? WHERE uuid = ?',
                   (category.name, category.description, category.parent, category.uuid))
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


os.system("mkdir /pwncrates/db 2>/dev/null")
os.system("touch /pwncrates/db/pwncrates.db")

if app.debug:
    app.logger.warning("App is running in debug mode, SQLite3 thread checks turned off")
    conn = sqlite3.connect('./db/pwncrates.db', check_same_thread=False)
else:
    # This *should* not cause any conflict, each worker has its own connection. The only conflict is when the git thread
    # attempts changes. Which happens in a separate thread.
    conn = sqlite3.connect('./db/pwncrates.db', check_same_thread=True)

try:
    if os.path.getsize("./db/pwncrates.db") == 0:
        initialize_database()
except sqlite3.OperationalError:
    # Here we assume a different worker beat us to it, though we should find a better solution.
    pass

update_database()
