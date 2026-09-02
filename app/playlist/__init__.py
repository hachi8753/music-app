from flask import Blueprint

playlist_bp = Blueprint("playlist", __name__, url_prefix = "/playlist", )

from . import routes
