from functools import wraps
from flask import abort
from flask_login import login_required, current_user


def super_admin_required(view):
    """Solo el super admin (config SUPER_ADMIN_USERNAME) puede acceder."""

    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not getattr(current_user, 'is_super_admin', False):
            abort(403)
        return view(*args, **kwargs)

    return wrapped
