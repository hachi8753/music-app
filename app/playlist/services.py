
from ..integrations.apple_music import get_all_playlists
from ..utils.converter import parse_iso_datetime
from ..extensions import db
from ..models import Playlist, UserPlaylist

def sync_playlists(user):
    
    print("sync_playlists")
    
    # Apple MusicからすべてのPlaylistを取得
    playlists = get_all_playlists(user)
    #print(playlists)
    
    current_ids = {
        playlist.get("id") for playlist in playlists
    }
    # DB上のPlaylist
    user_playlists = (
        db.session.query(UserPlaylist)
        .filter(UserPlaylist.user_id == user.id)
        .filter(UserPlaylist.is_library == True)
        .all()
    )
    
    # DB上に存在するがライブラリ上には存在しないプレイリストは、is_libraryをFalseにする
    for user_playlist in user_playlists:
        if user_playlist.playlist.apple_music_id not in current_ids:
            user_playlist.is_library = False
    
    # 各Playlistを同期
    for pl in playlists:
        
        # Playlistを同期
        sync_playlist(user, pl)
    
    db.session.commit()


def sync_playlist(user, playlist_data):
    
    data = playlist_data.get("attributes")
    apple_music_id = playlist_data.get("id")
    
    name = data.get("name")
    date_added = parse_iso_datetime(data.get("dateAdded"))
    last_modified_date = parse_iso_datetime(data.get("lastModifiedDate"))
    is_library = True
    can_edit = data.get("canEdit")
    
    #print(apple_music_id)
    if apple_music_id is None:
        return
    # DB内のPlaylistを取得
    playlist = (
        db.session.query(Playlist)
        .filter(
            Playlist.apple_music_id == apple_music_id, 
        )
        .first()
    )
    
    # Playlistを登録/更新
    if playlist:
        playlist.name = name
        playlist.last_modified_date = last_modified_date
    else:
        playlist = Playlist(
            name = name, 
            date_added = date_added, 
            last_modified_date = last_modified_date, 
            apple_music_id = apple_music_id, 
        )
        db.session.add(playlist)
        db.session.flush()

    # DB内のUserPlaylistを取得
    user_playlist = (
        db.session.query(UserPlaylist)
        .filter(
            UserPlaylist.user_id == user.id, 
            UserPlaylist.playlist_id == playlist.id, 
        )
        .first()
    )
    
    # UserPlaylistを登録/更新
    if user_playlist:
        user_playlist.is_library = is_library
        user_playlist.can_edit = can_edit
    else:
        user_playlist = UserPlaylist(
            user_id = user.id, 
            playlist_id = playlist.id, 
            is_library = is_library, 
            can_edit = can_edit, 
        )
        db.session.add(user_playlist)
        db.session.flush()

