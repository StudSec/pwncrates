"""
This file contains all API routes.

An API route is used either by external applications (for example the StudBot), or client side javascript.
"""
from flask_login import login_required, current_user
import webapp.database as db
from webapp import app
from flask import request
# General API file


@app.route('/api/get_users')
def api_get_users():
    return db.get_users()


@app.route('/api/challenges/categories')
def api_get_categories():
    return db.get_categories()


# TODO: refactor for JSON + update jinja2 from tuple -> dict
@app.route('/api/challenges/<category>')
def api_get_challenges(category):
    return db.get_challenges(category)


@app.route('/api/challenges/submit/<challenge_id>', methods=["POST"])
@login_required
def api_submit_challenge(challenge_id):
    try:
        return db.submit_flag(challenge_id, request.form['flag'], current_user.id)
    except KeyError:
        return "Flag missing."
