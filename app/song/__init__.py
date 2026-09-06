from flask import Blueprint

song_bp = Blueprint(
    "song",
    __name__, 
    url_prefix = "/songs", 
)

from . import routes
