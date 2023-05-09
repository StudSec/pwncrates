"""
This file contains objects used within the application
"""
from flask_login import UserMixin

import webapp.database as db


class User(UserMixin):
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username
        self.university = db.get_university(user_id)

    @staticmethod
    def get(user_id):
        user_name = db.get_username(user_id)
        if not user_name:
            return None
        return User(user_id, user_name)

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True
