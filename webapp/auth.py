"""
This file contains all routes and code relevant to authentication.

This includes authentication to the API endpoint, this allows us to easily modify authentication settings site-wide.
"""
import os
import sys
import time

from flask_login import LoginManager, login_user, login_required, logout_user
from flask import g, request, render_template, redirect, url_for, flash, session
from flask_login import current_user
from webapp.models import User
import webapp.database as db
from webapp import app
import requests
from . import mail
import json
import re
from functools import wraps

from urllib import parse

import bcrypt

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Read and eval config file
with open("config.json", "r") as f:
    config = json.loads(f.read())

REGISTRATION_ENABLED = config.get("registration_enabled", True)

CHALLENGES_PROTECTED = bool(config.get("challenges_behind_login", False))
# Challenges can optionally only be available for authenticated users
def challenge_protector(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if CHALLENGES_PROTECTED and not current_user.is_authenticated:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


# Login page
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            user_info = db.get_user(email=request.form["email"])

            if not user_info:
                flash('Invalid credentials')
                return render_template('login.html')

            password = user_info["password"]
            if not password:
                flash('Please reset password or use Oauth.')
                return render_template('login.html')

            if password == bcrypt.hashpw(request.form["password"].encode(), password.encode()).decode():
                # Check if user is still pending verification by checking the database
                if len(db.get_link_from_email(request.form["email"], "confirmation")) != 0:
                    flash('Account not yet activated')
                    return render_template('login.html')
                user = User(db.get_user(email=request.form["email"])["id"],
                            db.get_user(email=request.form["email"])["username"])
                login_user(user)
                time.sleep(0.5)  # Prevent a race condition, where the page loads but the user is not processed yet
                return redirect(url_for('challenges'))
        except KeyError:
            pass
        flash('Invalid credentials')
        return render_template('login.html', discord_oauth_enabled=len(config["oauth_client_secret"]))

    else:
        return render_template('login.html', discord_oauth_enabled=len(config["oauth_client_secret"]))


# Register page
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST" and REGISTRATION_ENABLED:
        try:
            # We check that the parameters are set before performing any actions
            username = request.form["username"]
            password = request.form["password"]
            email = request.form["email"]

            if db.get_user(email=email):
                flash("Email already taken")
                return render_template('register.html')

            if not re.match(r'^[\w\.+-]+@[\w\.-]+\.\w+$', email):
                flash('Invalid email')
                return render_template('register.html')

            # If no email server is set, we don't require a confirmation email.
            if config["SMTP_HOST"]:
                code = os.urandom(16).hex()
                db.insert_link(email, "confirmation", code)
                db.update_or_create_user(None, {
                    "username": username,
                    "password": bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('ascii'),
                    "email": email
                })

                if mail.confirm_email(email, f"https://{config['hostname']}{url_for('confirm_email')}?code={code}"):
                    flash('Failed to send confirmation email')
                    return render_template('register.html')
                message = "Registered, confirmation email sent."
            else:
                message = "Registered"

            db.update_or_create_user(None, {
                "username": username,
                "password": bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('ascii'),
                "email": email
            })

        except KeyError:
            return "Missing parameters"

        flash(message)
        return redirect(url_for('login'))
    else:
        if not REGISTRATION_ENABLED:
            flash("Registration is disabled.")
            return redirect(url_for('login'))
        return render_template('register.html')


@app.route('/password-reset', methods=["GET", "POST"])
def password_reset():
    code = request.args.get('code')

    if request.method == "POST":
        try:
            if "code" in request.form.keys():
                email = db.get_email_from_link("reset", request.form["code"])
                if not email:
                    return "Invalid code"

                email = email[0]

                if request.form["new_password"] != request.form["confirm_password"]:
                    return render_template("forgot_password.html", option="password", error="Passwords don't match")

                password = request.form["new_password"]
                db.update_or_create_user(db.get_user(email=email)["id"], {
                    "password": bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('ascii')
                })
                flash('Password changed')
                return redirect(url_for("login"))
            else:
                email = request.form["email"]
                code = os.urandom(16).hex()
                db.insert_link(email, "reset", code)

                mail.forgot_password(email, f"https://{config['hostname']}{url_for('password_reset')}?code={code}")

                flash("Reset link sent")
                return redirect(url_for('login'))
        except KeyError:
            return "Missing parameters"

    if code:
        if not db.get_email_from_link("reset", code):
            return "Invalid code"
        return render_template("forgot_password.html", option="password", code=code)
    else:
        return render_template("forgot_password.html")


@app.route('/confirm_email')
def confirm_email():
    code = request.args.get('code')

    if not code:
        return redirect(url_for("login"))

    if db.remove_link("confirmation", code):
        flash("Account activated")
        return redirect(url_for("login"))

    flash("Invalid code")
    return redirect(url_for("login"))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/discord/oauth')
def discord_oauth():
    if not config["oauth_client_secret"]:
        return redirect(url_for(login))
    base_url = "https://discord.com/oauth2/authorize"
    client_id = config["oauth_client_id"]
    redirect_uri = parse.quote_plus(config["oauth_redirect_uri"])
    scope = "identify%20email"
    session["discord_state"] = os.urandom(16).hex()
    return redirect(f"{base_url}?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope={scope}&"
                    f"state={session['discord_state']}")


@app.route('/discord/oauth_callback')
def discord_oauth_callback():
    state = request.args.get("state")
    code = request.args.get('code')

    if not state or "discord_state" not in session.keys() or state != session["discord_state"]:
        flash("Invalid OAuth flow.")
        session.pop("discord_state", None)
        return redirect(url_for("login"))
    else:
        session.pop("discord_state", None)

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
    discord_email = user_data.get("email")
    name = user_data.get("username")

    existing_email = db.get_user(discord_id=discord_id).get("email", "")
    stored_info = db.get_user(email=discord_email)

    # Register new user
    if not stored_info and not existing_email and not current_user.is_authenticated:
        if not REGISTRATION_ENABLED:
            flash('Registration is disabled.')
            return redirect(url_for('login'))
        db.update_or_create_user(None, {
            "username": name,
            "password": "",
            "email": discord_email,
            "discord_id": discord_id
        })

    # Link Discord to existing user
    elif not stored_info["discord_id"] and current_user.is_authenticated:
        db.update_or_create_user(current_user.id, {"discord_id": discord_id})

        return redirect(url_for('profile'))

    stored_info = db.get_user(discord_id=discord_id)
    user = User(stored_info["id"], stored_info["username"])
    login_user(user)
    time.sleep(0.5)  # Prevent a race condition, where the page loads but the user is not processed yet

    return redirect(url_for('challenges'))

