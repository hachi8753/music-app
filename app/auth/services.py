from werkzeug.security import generate_password_hash, check_password_hash

from ..extensions import db
from ..models import User


def register_user(username, email, password):

    # 重複チェック
    existing_user = db.session.query(User).filter(
        (User.username == username) |
        (User.email == email)
    ).first()

    if existing_user:
        return None

    # パスワードをハッシュ化
    password_hash = generate_password_hash(password)

    user = User(
        username=username,
        email=email,
        password_hash=password_hash,
    )

    db.session.add(user)
    db.session.commit()

    return user


def authenticate_user(username, password):

    user = db.session.query(User).filter_by(
        username=username
    ).first()

    if user is None:
        return None

    if not check_password_hash(
        user.password_hash,
        password,
    ):
        return None

    return user