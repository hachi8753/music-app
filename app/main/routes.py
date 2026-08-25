from flask import render_template

from . import main_bp
from ..auth.utils import login_required, get_current_user

@main_bp.route("/")
def index():
    return render_template("index.html")

@main_bp.route("/mypage")
@login_required
def mypage():
    
    user = get_current_user()
    
    return render_template(
        "mypage/index.html", 
        user = user
    )