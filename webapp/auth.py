"""
This file contains all routes and code relevant to authentication.

This includes authentication to the API endpoint, this allows us to easily modify authentication settings site-wide.
"""
import sys

from flask_login import LoginManager, login_user, login_required, logout_user
from flask import request, render_template, redirect, url_for, flash
from webapp.models import User
import webapp.database as db
from webapp import app
import requests
import json
import re

from urllib import parse

import bcrypt

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Read and eval config file
with open("config.json", "r") as f:
    config = json.loads(f.read())


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


# Login page
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_info = db.get_user(email=request.form["email"])

        if not user_info:
            flash('Invalid credentials')
            return render_template('login.html')

        password = user_info["password"]

        if password == bcrypt.hashpw(request.form["password"].encode(), password.encode()).decode():
            # Check if user is still pending verification by checking the database
            user = User(db.get_user(email=request.form["email"])["id"],
                        db.get_user(email=request.form["email"])["username"])
            login_user(user)
            return redirect(url_for('home'))

        flash('Invalid credentials')
        return render_template('login.html')

    else:
        return render_template('login.html')


# Register page
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if db.get_user(email=request.form["email"]):
            return render_template('register.html', error='Email already taken')

        if not re.match(r'^[\w\.+-]+@[\w\.-]+\.\w+$', request.form["email"]):
            return render_template('register.html', error='Invalid email')

        try:
            # Generate confirmation link
            # Insert it into database
            db.register_user(request.form["username"], bcrypt.hashpw(request.form["password"].encode(),
                                                                     bcrypt.gensalt()).decode('ascii'),
                             request.form["email"])
            # Send email
        except KeyError:
            return "Missing parameters"

        # Redirect to login

        user = User(db.get_user(email=request.form["email"])["id"],
                    db.get_user(email=request.form["email"])["username"])
        login_user(user)

        return redirect(url_for('challenges'))

    else:
        return render_template('register.html')


@app.route('/password_reset')
def password_reste():
    # If code parameter is set -> reset form
    # otherwise ask for email
    pass


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


# Generate the oauth url + redirect
@app.route('/discord/oauth')
def discord_oauth():
    base_url = "https://discord.com/oauth2/authorize"
    client_id = config["oauth_client_id"]
    redirect_uri = parse.quote_plus(config["oauth_redirect_uri"])
    scope = "identify%20email"
    return redirect(f"{base_url}?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope={scope}")


@app.route('/discord/oauth_callback')
def discord_oauth_callback():
    code = request.args.get('code')
    if not code:
        return redirect(url_for("login"))

    payload = {
        "client_id": config["oauth_client_id"],
        "client_secret": config["oauth_client_secret"],
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": config["oauth_redirect_uri"],
        "scope": "identify%20email"
    }

    access_token = requests.post(
        url="https://discord.com/api/oauth2/token",
        data=payload,
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )

    try:
        access_token = access_token.json().get("access_token")

        user_data = requests.get(url="https://discord.com/api/users/@me", headers={
            "Authorization": f"Bearer {access_token}"
        }).json()
        if "message" in user_data.keys() and user_data["message"] == '401: Unauthorized':
            flash('Discord auth failed.')
            return redirect(url_for('login'))
    except (ValueError, TypeError):
        return "invalid code"

    discord_id = user_data.get("id")
    email = user_data.get("email")
    name = user_data.get("username")

    stored_info = db.get_user(email=email)

    if not stored_info:
        db.register_user(name, "", email)
        db.update_discord_id(discord_id, email)

    elif stored_info["discord_id"] != discord_id:
        db.update_discord_id(discord_id, email)

    stored_info = db.get_user(email=email)
    user = User(stored_info["id"], stored_info["username"])
    login_user(user)

    return redirect(url_for('home'))

