"""
This file contains all API routes.

An API route is used either by external applications (for example the StudBot), or client side javascript.
"""
from webapp import app
import webapp.database as db
# General API file


@app.route('/api/get_users')
def get_users():
    return db.get_users()
