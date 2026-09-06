
from sqlalchemy import or_

from ..artist.services import register_artist
from ..album.services import register_album
from ..image.services import register_image, register_song_image
from ..image.presenters import get_main_image_path_of_song
from ..utils.converter import to_date
from ..utils.apple_music import get_relationship_id
from ..extensions import db
from ..models import Song, SongArtist, SongAlbum


def register_song(data) -> Song:
    
    attributes = data.get("attributes")
    # SongのCatalog Id
    apple_music_id = data.get("id")
    
    title = attributes.get("name")
    isrc = attributes.get("isrc")
    release_date = attributes.get("releaseDate")
    duration_in_millis = attributes.get("durationInMillis")
    artist_name = attributes.get("artistName")
    album_name = attributes.get("albumName")
    composer_name = attributes.get("composerName")
    has_lyrics = attributes.get("hasLyrics", False)
    apple_music_url = attributes.get("url")
    is_apple_digital_master = attributes.get("isAppleDigitalMaster", False)
    
    if isrc:
        song = db.session.query(Song).filter_by(isrc=isrc).first()
    elif apple_music_id:
        song = db.session.query(Song).filter_by(apple_music_id=apple_music_id).first()
    else:
        # apple_music_idがない場合は、title, artist_name, album_nameで検索
        song = (
            db.session.query(Song)
            .filter(
                Song.title == title,
                Song.artist_name == artist_name,
                Song.album_name == album_name,
            )
            .first()
        )
    
    if song:
        # 既存のSongを更新
        if title:
            song.title = title
        if isrc:
            song.isrc = isrc
        if release_date:
            song.release_date = to_date(release_date)
        if duration_in_millis:
            song.duration_in_millis = duration_in_millis
        if artist_name:
            song.artist_name = artist_name
        if album_name:
            song.album_name = album_name
        if composer_name:
            song.composer_name = composer_name
        if has_lyrics is not None:
            song.has_lyrics = has_lyrics
        if apple_music_url:
            song.apple_music_url = apple_music_url
        if is_apple_digital_master is not None:
            song.is_apple_digital_master = is_apple_digital_master
    else:
        # 新しいSongを作成
        song = Song(
            apple_music_id=apple_music_id,
            title=title,
            isrc=isrc,
            release_date=to_date(release_date),
            duration_in_millis=duration_in_millis,
            artist_name=artist_name,
            album_name=album_name,
            composer_name=composer_name,
            has_lyrics=has_lyrics,
            apple_music_url=apple_music_url,
            is_apple_digital_master=is_apple_digital_master,
        )
        db.session.add(song)

    db.session.flush()
    return song
    

def sync_songs(data_list) -> list[Song]:
    songs = []
    for data in data_list:
        song = register_song(data)
        songs.append(song)
        disc_number = data.get("attributes", {}).get("discNumber")
        track_number = data.get("attributes", {}).get("trackNumber")
        artwork = data.get("attributes", {}).get("artwork")
        
        image = register_image(artwork)
        register_song_image(song, image)
        
        artist = register_artist(make_artist_data(data))
        album = register_album(make_album_data(data))
        
        register_song_artist(song, artist)
        register_song_album(song, album, disc_number, track_number)
    
    db.session.commit()
    return songs


def make_artist_data(song_data):
    artist_id = get_relationship_id(song_data, "artists")
    if artist_id:
        return {
            "id": artist_id, 
            "attributes": {
                "name": song_data.get("attributes", {}).get("artistName")
            }
        }
    else:
        return {
            "attributes": {
                "name": song_data.get("attributes", {}).get("artistName")
            }
        }


def make_album_data(song_data):
    album_id = get_relationship_id(song_data, "albums")
    if album_id:
       return {
            "id": album_id,
            "attributes": {
                "name": song_data.get("attributes", {}).get("albumName")
            }
        }
    else:
        return {
            "attributes": {
                "name": song_data.get("attributes", {}).get("albumName")
            }
        }


def register_song_artist(song: Song, artist):
    song_artist = db.session.query(SongArtist).filter_by(song_id=song.id, artist_id=artist.id).first()
    
    if not song_artist:
        song_artist = SongArtist(song_id=song.id, artist_id=artist.id)
        db.session.add(song_artist)
    
    db.session.flush()
    return song_artist


def register_song_album(song: Song, album, disc_number=None, track_number=None):
    song_album = db.session.query(SongAlbum).filter_by(song_id=song.id, album_id=album.id).first()
    
    if not song_album:
        song_album = SongAlbum(
            song_id=song.id, 
            album_id=album.id,
            disc_number=disc_number,
            track_number=track_number
        )
        db.session.add(song_album)
    
    db.session.flush()
    return song_album


def get_songs_from_query(q):
    
    filters = [
        or_(
            Song.title.contains(q), 
            Song.artist_name.contains(q), 
            Song.album_name.contains(q)
        )
    ]
    
    songs = (
        db.session.query(Song)
        .filter(*filters)
        .order_by(Song.title.asc())
        .limit(30)
        .all()
    )
    
    return [
        {
            "id": song.id, 
            "title": song.title, 
            "image": get_main_image_path_of_song(song, 100, 100), 
        } for song in songs
    ]
    