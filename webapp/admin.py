"""
This file contains all routes and code relevant to admin functionality.
"""

from datetime import datetime, timezone, timedelta
from functools import wraps
import os
import random

from flask import (
    Blueprint, 
    request, 
    redirect, 
    url_for, 
    flash, 
    render_template
)
from flask_login import login_required, current_user

import webapp.database as db
from webapp import app
from webapp.auth import challenge_protector
from webapp.helpers import render_markdown
from webapp.models import User
from webapp.time_window import ctf_is_now, ctf_has_started, START_TIME, TIMEZONE

# Create Blueprint
admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """
    Custom decorator to check if the user is an admin.
    Redirects to 404 if user is not an admin.
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
    """Main admin dashboard view."""
    return render_template(
        "admin.html",
        users=db.get_scoreboard(),
        universities=db.get_scoreboard_universities()
    )

@admin_bp.route('/admin/hide_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def admin_hide_user(user_id):
    """Hide a user from the scoreboard."""
    # db.hide_user(user_id)  # Implement your hide functionality here
    flash(f"User {user_id} hidden from scoreboard.", "success")
    return redirect(url_for('admin'))

@admin_bp.route('/admin/demote_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def admin_demote_user(user_id):
    """Demote an admin to normal user."""
    if(current_user.id == str(user_id)):
        flash(f"Cannot demote yourself.", "warning")
    else:
        # db.demote_user(user_id)  # Implement the demotion functionality here
        flash(f"Admin {user_id} demoted to regular user.", "danger")
    return redirect(url_for('admin'))

@admin_bp.route('/admin/promote_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def admin_promote_user(user_id):
    """Promote a user to admin status."""
    if(current_user.id == str(user_id)):
        flash(f"You're already admin you silly.", "warning")
    else:
        # db.promote_user(user_id)  # Implement the promotion functionality here
        flash(f"User {user_id} promoted to admin.", "success")
    return redirect(url_for('admin'))


# Register Blueprint
app.register_blueprint(admin_bp)