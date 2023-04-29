"""
This file serves as the primary interface between the database and the rest of the code.

Sticking to this convention allows us to easily modify or switch the database without performing shotgun surgery.
"""
import mysql.connector

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
    cursor.execute('SELECT name, points, subcategory FROM challenges WHERE category = %s AND difficulty <= %s',
                   (category, difficulty))
    results = {}
    for (name, points, subcategory) in cursor:
        if subcategory in results.keys():
            results[subcategory].append((name, points))
        else:
            results[subcategory] = [(name, points)]
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
