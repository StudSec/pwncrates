"""
This file contains all API routes.

An API route is used either by external applications (for example the StudBot), or client side javascript.
"""
from webapp import app
from flask import request
import webapp.database as db
# General API file


@app.route('/api/get_users')
def api_get_users():
    return db.get_users()


@app.route('/api/challenges/categories')
def api_get_categories():
    return db.get_categories()


@app.route('/api/challenges/<category>')
def api_get_challenges(category):
    return db.get_challenges(category)


@app.route('/api/challenges/submit/<challenge_id>', methods=["POST"])
def api_submit_challenge(challenge_id):
    return db.submit_flag(challenge_id, request.form['flag'], 1)  # TODO: replace 1 with user id
