from flask import Blueprint

playlist_bp = Blueprint("playlist", __name__)

from . import routes
