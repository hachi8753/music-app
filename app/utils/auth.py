from flask import session

from ...app import User
from ...app import db

def get_current_user():
    user_id = session.get("user_id")

    if user_id is None:
        return None

    return db.session.query(User).filter_by(id=user_id).first()