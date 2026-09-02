from flask import render_template, redirect, url_for

from . import playlist_bp
from .services import sync_playlists
from ..auth.utils import login_required, get_current_user
from ..models import Playlist, SongPlaylist
from ..extensions import db

@playlist_bp.route("/")
@login_required
def index():
    return render_template("playlist/index.html")

@playlist_bp.route("/<int:playlist_id>")
@login_required
def detail(playlist_id: int):
    
    playlist = db.session.query(Playlist).filter_by(id=playlist_id).first()
    songs = db.session.query(SongPlaylist).filter(
        
    )
    
    return render_template(
        "playlist/detail.html", 
        playlist = playlist
    )


@playlist_bp.route("/sync", methods=['POST'])
@login_required
def sync():
    
    user = get_current_user()
    sync_playlists(user)
    
    return redirect(url_for('playlist.index'))