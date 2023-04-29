"""
This file contains all routes and code relevant to authentication.

This includes authentication to the API endpoint, this allows us to easily modify authentication settings site-wide.
"""
from webapp import app


# Login page
@app.route('/login')
def login():
    return ""


# Register page
@app.route('/register')
def register():
    return ""
