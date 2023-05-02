"""
This file contains objects used within the application
"""
import sys

from flask_login import UserMixin

import webapp.database as db


class User(UserMixin):
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username

    @staticmethod
    def get(user_id):
        print(f"getting user {user_id}", file=sys.stderr)
        user_name = db.get_username(user_id)
        if not user_name:
            print("returning None", file=sys.stderr)
            return None
        return User(user_id, user_name)

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True
