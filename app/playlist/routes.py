from flask import render_template, redirect, url_for, request

from . import playlist_bp
from .services import sync_playlists
from .presenters import build_playlist_detail
from ..auth.utils import login_required, get_current_user
from ..models import Playlist, SongPlaylist
from ..extensions import db

@playlist_bp.route("/")
@login_required
def index():
    
    page = request.args.get("page", 1, type=int)
    limit = 20
    offset = (page - 1) * limit
    limit = min(max(limit, 1), 100)
    
    playlists = (
        db.session.query(Playlist)
        .order_by(Playlist.last_modified_date.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    return render_template(
        "playlist/index.html", 
        playlists=playlists, 
    )

@playlist_bp.route("/<int:playlist_id>")
@login_required
def detail(playlist_id: int):
    
    page = request.args.get("page", 1, type=int)
    limit = 200
    offset = (page - 1) * limit
    limit = min(max(limit, 1), 100)
    
    context = build_playlist_detail(playlist_id, offset, limit)
    
    return render_template(
        "playlist/detail.html", 
        **context
    )


@playlist_bp.route("/sync", methods=['POST'])
@login_required
def sync():
    
    user = get_current_user()
    sync_playlists(user)
    
    return redirect(url_for('playlist.index'))