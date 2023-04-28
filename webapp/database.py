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
