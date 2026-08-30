
from ..integrations.apple_music import get_all_playlists
from ..utils.converter import parse_iso_datetime
from ..extensions import db
from ..models import Playlist, UserPlaylist

def sync_playlists(user):
    
    # Apple MusicからすべてのPlaylistを取得
    playlists = get_all_playlists(user)
    
    current_ids = {
        playlist.get("id") for playlist in playlists
    }
    
    # DB上のPlaylist
    user_playlists = (
        db.session.query(UserPlaylist)
        .filter(
            UserPlaylist.user_id == user.id,
            UserPlaylist.is_library == True
        )
        .all()
    )
    
    for user_playlist in user_playlists:
        if user_playlist.playlist.apple_music_id not in current_ids:
            user_playlist.is_library = False
    
    for pl in playlists:
        
        data = pl.get("attributes")
        
        name = data.get("name")
        date_added = parse_iso_datetime(data.get("dateAdded"))
        last_modefied_date = parse_iso_datetime(data.get("lastModifiedDate"))
        apple_music_id = pl.get("id")
        is_library = True
        can_edit = data.get("canEdit")
        
        if apple_music_id is not None:
            continue
        
        playlist = (
            db.session.query(Playlist)
            .filter(
                Playlist.apple_music_id == apple_music_id, 
            )
            .first()
        )
        
        if playlist:
            playlist.name = name
            playlist.last_modified_date = last_modefied_date
        else:
            playlist = Playlist(
                name = name, 
                date_added = date_added, 
                last_modefied_date = last_modefied_date, 
                apple_music_id = apple_music_id, 
            )
            db.session.add(playlist)
            db.session.flush()
            user_playlist = UserPlaylist(
                user_id = user.id, 
                is_library = is_library, 
                can_edit = can_edit, 
            )
    
    db.session.commit()
    