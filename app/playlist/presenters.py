
from ..image.presenters import get_image_path
from ..extensions import db
from ..models import Playlist, SongPlaylist, Song, PlaylistImage, SongImage



def build_playlist_detail(playlist_id, offset, limit):
    
    playlist = db.session.query(Playlist).filter_by(id=playlist_id).first()
    
    song_playlists = (
        db.session.query(SongPlaylist)
        .filter(SongPlaylist.playlist_id == playlist_id)
        .order_by(SongPlaylist.position)
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    songs_list = []
    
    for song_playlist in song_playlists:
        main_song_image = (
            db.session.query(SongImage)
            .filter(
                SongImage.song_id == song_playlist.song_id, 
                SongImage.is_main == True, 
            )
            .first()
        )
        
        image_path = (
            get_image_path(main_song_image.image, 100, 100)
            if main_song_image else None
        )
        
        songs_list.append({
            "song": song_playlist.song, 
            "path": image_path, 
        })
    
    
    return {
        'playlist': playlist, 
        'song_data_list': songs_list, 
    }
