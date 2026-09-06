
from ..song.services import sync_songs, register_song
from ..image.services import register_image, register_playlist_image, register_song_image
from ..integrations.apple_music import get_all_playlists, get_all_playlist_songs, get_songs
from ..utils.converter import parse_iso_datetime, to_date, to_utc_naive
from ..extensions import db
from ..models import Playlist, UserPlaylist, SongPlaylist, UserSong, PlaylistSnapshot, PlaylistSnapshotSong

from datetime import datetime, timezone
from pprint import pprint

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
    last_modified_date = to_utc_naive(parse_iso_datetime(data.get("lastModifiedDate")))
    is_library = True
    can_edit = data.get("canEdit")
    artwork = data.get("artwork")
    
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
    
    # PlaylistImageを登録
    if artwork:
        image = register_image(artwork)
        register_playlist_image(playlist, image)
    
    # PlaylistSongを取得
    last_playlist_snapshot = (
        db.session.query(PlaylistSnapshot)
        .filter_by(playlist_id=playlist.id)
        .order_by(PlaylistSnapshot.snapshot_date.desc())
        .first()
    )
    
    last_modified_date = playlist.last_modified_date.replace(tzinfo=None)
    snapshot_date = last_playlist_snapshot.snapshot_date if last_playlist_snapshot else None
    if (
        last_playlist_snapshot is None
        or playlist.last_modified_date > snapshot_date
    ):
        # tracks の取得処理
        sync_playlist_songs(user, playlist)

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


def sync_playlist_songs(user, playlist):
    
    # APIからPlaylistの曲情報を取得
    playlist_songs = get_all_playlist_songs(user, playlist)
    
    # PlaylistSnapshotを作成
    playlist_snapshot = PlaylistSnapshot(
        playlist_id=playlist.id,
        snapshot_date=datetime.now(timezone.utc).replace(tzinfo=None),
    )
    db.session.add(playlist_snapshot)
    db.session.flush()

    # playlist_songsに含まれるcatalog_idを集合の形で取得
    song_catalog_ids = set()
    for position, data in enumerate(playlist_songs):
        attributes = data.get("attributes") or {}
        play_params = attributes.get("playParams") or {}
        catalog_id = play_params.get("catalogId")
        if catalog_id:
            song_catalog_ids.add(catalog_id)

    # Songを取得
    songs_data = get_songs(list(song_catalog_ids))
    songs = sync_songs(songs_data)
    songs_map = {
        song.apple_music_id: song for song in songs
    }
    print(len(songs))
    
    # PlaylistSongを登録/更新
    for position, data in enumerate(playlist_songs):
        attributes = data.get("attributes") or {}
        play_params = attributes.get("playParams") or {}
        catalog_id = play_params.get("catalogId")
        
        if catalog_id:
            song = songs_map.get(catalog_id)
            if not song:
                print(f"Song not found for catalog_id: {catalog_id}")
                song = register_song({
                    "id": catalog_id, 
                    "attributes": attributes,
                })
                image = register_image(attributes.get("artwork"))
                register_song_image(song, image)
        else:
            song = register_song({
                "id": None, 
                "attributes": attributes,
            })
            image = register_image(attributes.get("artwork"))
            register_song_image(song, image)
        
        # PlaylistSongを登録/更新
        song_playlist = (
            db.session.query(SongPlaylist)
            .filter(
                SongPlaylist.playlist_id == playlist.id, 
                SongPlaylist.position == position, 
            )
            .first()
        )
        if song_playlist:
            song_playlist.song_id = song.id
        else:
            song_playlist = SongPlaylist(
                playlist_id = playlist.id, 
                song_id = song.id, 
                position = position, 
            )
            db.session.add(song_playlist)
        
        # PlaylistSnapshotSongを登録
        snapshot_song = PlaylistSnapshotSong(
            snapshot_id = playlist_snapshot.id, 
            song_id = song.id, 
            position = position, 
        )
        db.session.add(snapshot_song)
        
        # UserSongを登録/更新
        user_song = (
            db.session.query(UserSong)
            .filter(
                UserSong.user_id == user.id, 
                UserSong.song_id == song.id, 
            )
            .first()
        )
        if not user_song:
            user_song = UserSong(
                user_id = user.id, 
                song_id = song.id, 
                first_listened_at = to_date(datetime.now()),
                is_library = play_params.get("isLibrary", True),
                apple_library_id = data.get("id"),
            )
            db.session.add(user_song)
        else:
            user_song.is_library = play_params.get("isLibrary", True)
            user_song.apple_library_id = data.get("id")
    
    # 削除されたplaylist, positionの組み合わせをDBから削除
    deleted_song_playlists = (
        db.session.query(SongPlaylist)
        .filter(
            SongPlaylist.playlist_id == playlist.id, 
            SongPlaylist.position > len(playlist_songs) - 1, 
        )
        .all()
    )
    for song_playlist in deleted_song_playlists:
        db.session.delete(song_playlist)
    
    db.session.flush()