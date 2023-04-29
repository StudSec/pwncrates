"""
This file serves as the primary interface between the database and the rest of the code.

Sticking to this convention allows us to easily modify or switch the database without performing shotgun surgery.
"""
import mysql.connector
import time

config = {
    'user': 'root',
    'password': 'root',
    'host': 'db',
    'port': '3306',
    'database': 'pwncrates'
}


def get_users():
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM users')
    results = [{name: color} for (name, color) in cursor]
    cursor.close()
    connection.close()

    return results


def get_challenges(category, difficulty="hard"):
    difficulties = {
        "easy": 1,
        "medium": 2,
        "hard": 3
    }
    # Translate the difficulty to int
    difficulty = difficulties[difficulty.lower()]

    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute('SELECT id, name, description, points, subcategory FROM challenges '
                   'WHERE category = %s AND difficulty <= %s',
                   (category, difficulty))
    results = {}
    for (id, name, description, points, subcategory) in cursor:
        if subcategory in results.keys():
            results[subcategory].append((id, name, description, points))
        else:
            results[subcategory] = [(id, name, description, points)]
    cursor.close()
    connection.close()

    return results


def get_categories():
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute('SELECT DISTINCT category FROM challenges;')
    results = [category[0] for category in cursor]
    cursor.close()
    connection.close()

    return results


def submit_flag(challenge_id, flag, user_id):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute('SELECT DISTINCT flag FROM challenges WHERE id = %s AND flag = %s;', (challenge_id, flag))

    if cursor.fetchone():
        cursor.execute('SELECT id FROM solves WHERE challenge_id = %s AND user_id = %s;', (challenge_id, user_id))
        if cursor.fetchone():
            ret = "Already solved"
        else:
            cursor.execute('INSERT INTO solves (challenge_id, solved_time, user_id) VALUES (%s, %s, %s);',
                           (challenge_id, int(time.time()), user_id))
            cursor.execute('UPDATE challenges SET solves = solves + 1 WHERE id = %s', (challenge_id,))
            cursor.execute('UPDATE users U SET U.points = U.points + '
                           '(SELECT points FROM challenges WHERE id = %s) '
                           'WHERE id = %s', (challenge_id, user_id))
            connection.commit()
            ret = "OK"
    else:
        ret = "Incorrect flag"

    cursor.close()
    connection.close()

    return ret


def get_scoreboard():
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute('SELECT name, points FROM users ORDER BY points DESC;')
    results = [user for user in cursor]
    cursor.close()
    connection.close()

    return results


