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

import pwncrates.database as db
from pwncrates import app
from pwncrates.auth import challenge_protector
from pwncrates.helpers import render_markdown
from pwncrates.models import User
from pwncrates.time_window import ctf_is_now, ctf_has_started, START_TIME, TIMEZONE

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
        users=db.get_users(),
        #universities=db.get_scoreboard_universities()
    )

def validate_user_id(user_id):
    """Helper function to validate and convert user_id to integer."""
    try:
        return int(user_id)
    except ValueError:
        flash("Invalid user ID. Please try again.", "danger")
        return None  # Return None if the conversion fails

@admin_bp.route('/admin/toggle_user_visibility/<user_id>/<action>', methods=['POST'])
@login_required
@admin_required
def admin_toggle_user_visibility(user_id, action):
    """Toggle user visibility in the scoreboard."""
    user_id = validate_user_id(user_id)
    if user_id is None:
        return redirect(url_for('admin'))

    if action == 'hide':
        db.hide_user(user_id)
        message = f"User {user_id} hidden from scoreboard."
    elif action == 'show':
        db.show_user(user_id)
        message = f"User {user_id} is now on the scoreboard."
    else:
        flash("Invalid action specified.", "error")
        return redirect(url_for('admin'))

    flash(message, "success")
    return redirect(url_for('admin'))


@admin_bp.route('/admin/demote_user/<user_id>', methods=['POST'])
@login_required
@admin_required
def admin_demote_user(user_id):
    """Demote an admin to normal user."""
    user_id = validate_user_id(user_id)
    if user_id is None:
        return redirect(url_for('admin'))

    if int(current_user.id) == user_id:
        flash(f"Cannot demote yourself.", "warning")
    else:
        db.demote_user(user_id)  # Implement the demotion functionality here
        flash(f"Admin {user_id} demoted to regular user.", "danger")
    return redirect(url_for('admin'))

@admin_bp.route('/admin/promote_user/<user_id>', methods=['POST'])
@login_required
@admin_required
def admin_promote_user(user_id):
    """Promote a user to admin status."""
    user_id = validate_user_id(user_id)
    if user_id is None:
        return redirect(url_for('admin'))

    if int(current_user.id) == user_id:
        flash(f"You're already admin, you silly.", "warning")
    else:
        db.promote_user(user_id)  # Implement the promotion functionality here
        flash(f"User {user_id} promoted to admin.", "success")
    return redirect(url_for('admin'))


# Register Blueprint
app.register_blueprint(admin_bp)