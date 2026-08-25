from flask import Flask

from .extensions import db, migrate
from . import models

def create_app():
    app = Flask(__name__)

    # 設定
    app.config.from_object("config.Config")

    # extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Blueprint
    from .main import main_bp
    from .auth import auth_bp
    from .playlist import playlist_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(playlist_bp)

    return app