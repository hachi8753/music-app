import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# 設定
# ============================================================

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # デバッグモード
    DEBUG=True
    # 警告対策
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # DB設定
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "instance", "music.sqlite")
    SECRET_KEY = os.urandom(24)

# class Config:
#     SECRET_KEY = os.environ.get("SECRET_KEY")
#     SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
#     SQLALCHEMY_TRACK_MODIFICATIONS = False