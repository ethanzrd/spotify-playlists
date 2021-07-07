from functools import wraps

from flask_login import current_user
from flask import abort


def logout_required(func):
    """Checks whether user is logged out or raises error 401."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated:
            abort(401)
        return func(*args, **kwargs)

    return wrapper
