"""
This file contains all routes and code relevant to authentication.

This includes authentication to the API endpoint, this allows us to easily modify authentication settings site-wide.
"""
from flask_login import LoginManager, login_user, login_required, logout_user
from flask import request, render_template, redirect, url_for
from webapp.models import User
import webapp.database as db
from webapp import app

import bcrypt


login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


# Login page
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = db.get_password(request.form["username"])

        if not password:
            return render_template('login.html', error='Invalid credentials')
        if password == bcrypt.hashpw(request.form["password"].encode(), password.encode()).decode():
            user = User(db.get_id(request.form["username"]), request.form["username"])
            login_user(user)
            return redirect(url_for('home'))

        return render_template('login.html', error='Invalid credentials')

    else:
        return render_template('login.html')


# Register page
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Check if user exists
        if db.get_id(request.form["username"]):
            return render_template('register.html', error='User already exists.')

        db.register_user(request.form["username"], bcrypt.hashpw(request.form["password"].encode(),
                                                                 bcrypt.gensalt()).decode('ascii'))
        user = User(db.get_id(request.form["username"]), request.form["username"])
        login_user(user)
        return redirect(url_for('challenges'))

    else:
        return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))
