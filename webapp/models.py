"""
This file contains objects used within the application
"""
import sys

from flask_login import UserMixin

import webapp.database as db


class User(UserMixin):
    def __init__(self, user_id, username):
        db_info = db.get_user(user_id=user_id)
        self.id = user_id
        self.username = username
        self.university = db_info["university_name"]
        self.discord_id = db_info["discord_id"]
        self.admin = True #db_info["admin"]
        self.authenticated = True

    @staticmethod
    def get(user_id):
        user_info = db.get_user(user_id=user_id)
        if not user_info:
            return None
        return User(user_id, user_info["username"])

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return self.authenticated

    @property
    def is_admin(self):
        return self.admin

    def get_user_information(self):
        pass
