from functools import wraps

from flask import redirect, session, url_for

from app.models import User
from app import db


def get_current_user():
    user_id = session.get("user_id")

    if user_id is None:
        return None

    return db.session.query(User).filter_by(id=user_id).first()


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        user = get_current_user()

        if user is None:
            print("login_required: user is none")
            return redirect(url_for("auth.login"))

        return view(*args, **kwargs)

    return wrapped_view