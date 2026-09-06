from flask import Blueprint

award_bp = Blueprint(
    "award",
    __name__, 
    url_prefix = "/awards", 
)

from . import routes
