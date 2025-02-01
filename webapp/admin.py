"""
This file contains all routes and code relevant to admin.

"""

from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_required, current_user
import webapp.database as db
from webapp import app

admin_bp = Blueprint('admin', __name__)

from flask import redirect, url_for


import os

from webapp import app
from flask import render_template, request, redirect, url_for
from flask_login import current_user, login_required
import webapp.database as db
from webapp.helpers import render_markdown
from webapp.models import User
from webapp.time_window import ctf_is_now, ctf_has_started, START_TIME, TIMEZONE
from datetime import datetime, timezone, timedelta
from webapp.auth import challenge_protector
import random
from functools import wraps
from flask import redirect, url_for

def admin_required(f):
    """
    Custom decorator to check if the user is an admin.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
         
        if not current_user.is_admin:
            return render_template('404.html'), 404
        
        return f(*args, **kwargs)
    
    return decorated_function


@app.route('/admin')
@login_required
@admin_required
def admin():
    return render_template("admin.html", users=db.get_scoreboard(), universities=db.get_scoreboard_universities())


@admin_bp.route('/admin/hide_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def admin_hide_user(user_id):
    if not current_user.is_admin:
        flash("You do not have permission to perform this action.", "danger")
        return redirect(url_for('admin'))
    
    db.hide_user(user_id)
    flash("User hidden from scoreboard.", "success")
    return redirect(url_for('admin'))

@admin_bp.route('/admin/ban_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def admin_ban_user(user_id):
    if not current_user.is_admin:
        flash("You do not have permission to perform this action.", "danger")
        return redirect(url_for('admin'))
    
    db.ban_user(user_id)
    flash("User banned.", "success")
    return redirect(url_for('admin'))

@admin_bp.route('/admin/promote_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def admin_promote_user(user_id):
    if not current_user.is_admin:
        flash("You do not have permission to perform this action.", "danger")
        return redirect(url_for('admin'))
    
    db.promote_user(user_id)
    flash("User promoted.", "success")
    return redirect(url_for('admin'))

# Register Blueprint
app.register_blueprint(admin_bp)
