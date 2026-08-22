from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import func, JSON
import pytz

# 日本時間のタイムゾーン設定
jst = pytz.timezone("Asia/Tokyo")
# 現在のUTC時間を取得し、日本時間に変換
now_jst = datetime.now(pytz.utc).astimezone(jst)

# Flask-SQLAlchemyの生成
db = SQLAlchemy()

class Song:
    __tablename__ = 'songs'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    
    

class Artist:
    __tablename__ = 'artists'