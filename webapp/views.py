"""
This file handles all non-API and non-auth routes
"""
from webapp import app
from flask import render_template


# Home page
@app.route('/')
def home():
    return render_template("home.html")


# Rule page
@app.route('/rules')
def rules():
    return ""


# Contributing page
@app.route('/contributing')
def contributing():
    return ""


# General category page, contains an overview of the categories if no category is specified
@app.route('/challenges')
@app.route('/challenges/<category>')
def challenges(category=None):
    return ""


# Writeups page, contains an overview of all available writeups if no challenge is specified.
@app.route('/writeups')
@app.route('/writeups/<challenge>')
def writeups(challenge=None):
    return ""
