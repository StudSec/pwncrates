import datetime
import re
import csv
import sqlite3
conn = sqlite3.connect("../data/db/pwncrates.db")
with open("backup.sql", "r") as f:
    old_database = f.read().split(";\n")

# Insert users & create lookup table
user_lookup = {}
for statement in old_database:
    if statement.startswith("INSERT INTO `users` VALUES"):
        users = re.findall(r'\((.*?)\)', statement)
        for user in users:
            user_data = list(csv.reader([user], delimiter=',', quotechar="'"))[0]
            username = user_data[2]
            email = user_data[4]
            old_id = user_data[0]

            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users (name, email) VALUES (?, ?);", (username, email))
                user_lookup[str(old_id)] = str(cursor.lastrowid)
                cursor.close()
            except sqlite3.IntegrityError:
                cursor.execute("SELECT id FROM users WHERE email = ?;", (email,))
                user_lookup[str(old_id)] = str(cursor.fetchone()[0])
                cursor.close()
                continue

        conn.commit()

# Create challenge lookup table old_id -> new id
challenge_lookup = {}
for statement in old_database:
    if statement.startswith("INSERT INTO `challenges` VALUES"):
        challenges = re.findall(r'\((.*?)\)', statement)
        for challenge in challenges:
            challenge_data = list(csv.reader([challenge], delimiter=',', quotechar="'"))[0]

            if len(challenge_data) < 2:
                continue

            challenge_old_id = challenge_data[0]
            challenge_name = challenge_data[1]

            cursor = conn.cursor()
            # Casing might have changed
            cursor.execute("SELECT id FROM challenges WHERE name COLLATE NOCASE = ?;", (challenge_name,))
            challenge_new_id = cursor.fetchone()
            if not challenge_new_id or len(challenge_new_id) == 0:
                print(f"Could not find challenge {challenge_name.encode()} with id {challenge_old_id} "
                      f"add manually if needed")
                continue
            challenge_lookup[str(challenge_old_id)] = str(challenge_new_id[0])

# Manual
# challenge_lookup["19"] = "31"


# Get submission times
submission_lookup = {}
for statement in old_database:
    if statement.startswith("INSERT INTO `submissions` VALUES"):
        submissions = re.findall(r'\((.*?)\)', statement)
        for submission in submissions:
            submission_data = list(csv.reader([submission], delimiter=',', quotechar="'"))[0]

            # A bit hacky, but some flag submissions cause csv reader to bug out for reasons unknown
            # to me. As a workaround we can ignore any submission that's malformed.
            try:
                if submission_data[6] != "correct":
                    continue
            except IndexError:
                print(f"malformed submission, skipping {submission}")
                continue
            old_challenge_id = submission_data[1]
            old_user_id = submission_data[2]
            submission_type = submission_data[6]
            submission_date = submission_data[7]

            submission_lookup[(old_challenge_id, old_user_id)] = int(
                datetime.datetime.strptime(submission_date, '%Y-%m-%d %H:%M:%S.%f').strftime('%s')
            )

# Update solves table
for statement in old_database:
    if statement.startswith("INSERT INTO `solves` VALUES"):
        solves = re.findall(r'\((.*?)\)', statement)
        for solve in solves:
            solve_data = list(csv.reader([solve], delimiter=',', quotechar="'"))[0]
            solve_challenge_id = solve_data[1]
            solve_user_id = solve_data[2]

            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO solves (challenge_id, solved_time, user_id) VALUES (?, ?, ?);",
                               (challenge_lookup[solve_challenge_id],
                                submission_lookup[(solve_challenge_id, solve_user_id)],
                                user_lookup[solve_user_id]))
            except (sqlite3.IntegrityError, KeyError):
                pass
            cursor.close()

        conn.commit()

# Optional: If the discord plugin is present we want to associate each discord id to its relevant account.
for statement in old_database:
    if statement.startswith("INSERT INTO `discorduser` VALUES"):
        discord_users = re.findall(r'\((.*?)\)', statement)
        for discord_user in discord_users:
            discord_data = list(csv.reader([discord_user], delimiter=',', quotechar="'"))[0]
            old_user_id = discord_data[0]
            discord_id = discord_data[2]

            cursor = conn.cursor()
            try:
                cursor.execute("UPDATE users SET discord_id = ? WHERE ID = ?;",
                               (discord_id,
                                user_lookup[old_user_id]))
            except (sqlite3.IntegrityError, KeyError):
                pass
            cursor.close()

        conn.commit()
