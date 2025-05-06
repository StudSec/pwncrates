"""
Testing if database migrations work
"""
import pytest
import sqlite3
import os


def test_migration():
    latest_migration = max([float(x.split("-")[2][:-4]) for x in os.listdir("/pwncrates/database/") if x.startswith("migration-")])

    print(os.listdir("/pwncrates/db"))
    conn = sqlite3.connect('/pwncrates/db/pwncrates.db')
    cursor = conn.cursor()
    cursor.execute("SELECT version FROM pwncrates")
    database_version = float(cursor.fetchone()[0])

    assert latest_migration == database_version