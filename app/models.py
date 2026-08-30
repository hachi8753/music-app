from datetime import datetime
import pytz

from .extensions import db

# 日本時間のタイムゾーン設定
jst = pytz.timezone("Asia/Tokyo")
# 現在のUTC時間を取得し、日本時間に変換
now_jst = datetime.now(pytz.utc).astimezone(jst)

# ============================================================================
# メインモデル
# ============================================================================

class Song(db.Model):
    __tablename__ = "songs"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    
    apple_music_id = db.Column(db.String(20), unique=True, nullable=True)
    isrc = db.Column(db.String, unique=True, nullable=True)
    
    duration_in_millis = db.Column(db.Integer)
    release_date = db.Column(db.Date)
    
    created_at = db.Column(db.DateTime, default=lambda: now_jst)
    updated_at = db.Column(db.DateTime, default=lambda: now_jst, onupdate=lambda: now_jst)
    
    artists = db.relationship(
        "Artist", 
        secondary = "song_artists", 
        back_populates = "songs"
    )
    
    albums = db.relationship(
        "Album", 
        secondary = "song_albums", 
        back_populates = "songs"
    )
    
    playlists = db.relationship(
        "Playlist", 
        secondary = "song_playlists", 
        back_populates = "songs"
    )
    
    work_id = db.Column(
        db.Integer, 
        db.ForeignKey("works.id"), 
        nullable = True
    )
    work = db.relationship("Work", back_populates="songs")
    
    user_songs = db.relationship(
        "UserSong", 
        back_populates = "song", 
        cascade = "all, delete-orphan", 
    )
    users = db.relationship(
        "User", 
        secondary = "user_songs", 
        viewonly = True, 
    )
    
    images = db.relationship(
        "SongImage", 
        back_populates = "song"
    )

class Artist(db.Model):
    __tablename__ = "artists"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    name_en = db.Column(db.String(255))
    
    apple_music_id = db.Column(db.String(20), unique=True, nullable=True)
    
    created_at = db.Column(db.DateTime, default=lambda: now_jst)
    updated_at = db.Column(db.DateTime, default=lambda: now_jst, onupdate=lambda: now_jst)
        
    
    songs = db.relationship(
        "Song", 
        secondary = "song_artists", 
        back_populates = "artists"
    )
    
    albums = db.relationship(
        "Album", 
        secondary="artist_albums", 
        back_populates = "artists"
    )
    user_artists = db.relationship(
        "UserArtist", 
        back_populates = "artist"
    )

    images = db.relationship(
        "ArtistImage", 
        back_populates = "artist"
    )

class Album(db.Model):
    __tablename__ = "albums"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255))
    
    apple_music_id = db.Column(db.String(20), unique=True, nullable=True)
    
    is_compilation = db.Column(db.Boolean)
    is_single = db.Column(db.Boolean)
    release_date = db.Column(db.Date)
    
    created_at = db.Column(db.DateTime, default=lambda: now_jst)
    updated_at = db.Column(db.DateTime, default=lambda: now_jst, onupdate=lambda: now_jst)
    
    songs = db.relationship(
        "Song", 
        secondary = "song_albums", 
        back_populates = "albums"
    )
    
    artists = db.relationship(
        "Artist", 
        secondary = "artist_albums", 
        back_populates = "albums"
    )
    
    images = db.relationship(
        "AlbumImage", 
        back_populates = "album"
    )


class Work(db.Model):
    __tablename__ = "works"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255))
    
    created_at = db.Column(db.DateTime, default=lambda: now_jst)
    updated_at = db.Column(db.DateTime, default=lambda: now_jst, onupdate=lambda: now_jst)
    
    songs = db.relationship(
        "Song", 
        back_populates = "work"
    )
    

class Playlist(db.Model):
    __tablename__ = "playlists"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    
    date_added = db.Column(db.DateTime(timezone=True))
    last_modified_date = db.Column(db.DateTime(timezone=True))
    apple_music_id = db.Column(db.String)
    
    created_at = db.Column(db.DateTime, default=lambda: now_jst)
    updated_at = db.Column(db.DateTime, default=lambda: now_jst, onupdate=lambda: now_jst)
    
    users = db.relationship(
        "User",
        secondary = "user_playlists", 
        view_only = True
    )
    user_playlists = db.relationship(
        "UserPlaylist", 
        back_populates = "playlist", 
        cascade = "all, delete-orphan", 
    )
    
    songs = db.relationship(
        "Song", 
        secondary = "song_playlists", 
        back_populates = "playlists"
    )

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50))
    
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    apple_music_user_token = db.Column(db.Text, nullable=True)
    
    role = db.Column(
        db.Enum("user", "admin", name="user_role"), 
        nullable=False, 
        default="user", 
    )
    
    created_at = db.Column(db.DateTime, default=lambda: now_jst)
    updated_at = db.Column(db.DateTime, default=lambda: now_jst, onupdate=lambda: now_jst)

    
    playlists = db.relationship(
        "Playlist", 
        secondary = "user_playlists", 
        view_only = True
    )
    user_playlists = db.relationship(
        "UserPlaylist", 
        back_populates = "user", 
        cascade = "all, delete-orphan", 
    )
    
    # 中間テーブルUserSongへの参照
    user_songs = db.relationship(
        "UserSong", 
        back_populates = "user", 
        cascade = "all, delete-orphan", 
    )
    songs = db.relationship(
        "Song", 
        secondary = "user_songs", 
        viewonly = True, 
    )
    user_artists = db.relationship(
        "UserArtist", 
        back_populates = "user"
    )

# ============================================================================
# 中間テーブル
# ============================================================================

# Song と Artist の中間テーブル
song_artist = db.Table(
    "song_artists",
    db.Column(
        "song_id",
        db.Integer,
        db.ForeignKey("songs.id", ondelete="CASCADE", name="fk_song_artists_song_id_songs"),
        primary_key=True
    ),
    db.Column(
        "artist_id",
        db.Integer,
        db.ForeignKey("artists.id", ondelete="CASCADE", name="fk_song_artists_artist_id_artists"),
        primary_key=True
    )
)

# Song と Album の中間テーブル
class SongAlbum(db.Model):
    __tablename__ = "song_albums"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    album_id = db.Column(
        db.Integer, 
        db.ForeignKey(
            "albums.id", 
            ondelete = "CASCADE", 
            name = "fk_song_albums_album_id_albums", 
        )
    )
    song_id = db.Column(
        db.Integer, 
        db.ForeignKey(
            "songs.id", 
            ondelete = "CASCADE", 
            name = "fk_song_albums_song_id_songs", 
        )
    )
    disc_number = db.Column(
        db.Integer, 
        nullable = True, 
        default = 1, 
    )
    track_number = db.Column(
        db.Integer, 
        nullable = True
    )
    created_at = db.Column(db.DateTime, default=lambda: now_jst)

# Artist と Album の中間テーブル
artist_album = db.Table(
    "artist_albums",
    db.Column(
        "album_id",
        db.Integer,
        db.ForeignKey("albums.id", ondelete="CASCADE", name="fk_artist_albums_album_id_albums"),
        primary_key=True
    ),
    db.Column(
        "artist_id",
        db.Integer,
        db.ForeignKey("artists.id", ondelete="CASCADE", name="fk_artist_albums_artist_id_artists"),
        primary_key=True
    )
)

# Song と Playlist の中間テーブル
class SongPlaylist(db.Model):
    __tablename__ = "song_playlists"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    playlist_id = db.Column(
        db.Integer, 
        db.ForeignKey(
            "playlists.id", 
            ondelete = "CASCADE", 
            name = "fk_song_playlists_playlist_id_playlists", 
        )
    )
    song_id = db.Column(
        db.Integer, 
        db.ForeignKey(
            "songs.id", 
            ondelete = "CASCADE", 
            name = "fk_song_playlists_song_id_songs", 
        )
    )

    position = db.Column(
        db.Integer, 
        nullable = True
    )
    created_at = db.Column(db.DateTime, default=lambda: now_jst)
    updated_at = db.Column(db.DateTime, default=lambda: now_jst, onupdate=lambda: now_jst)

# ============================================================================
# 中間テーブル (User)
# ============================================================================

# UserとSongの関連を定義
class UserSong(db.Model):
    __tablename__ = "user_songs"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    user_id = db.Column(
        db.Integer, 
        db.ForeignKey("users.id")
    )
    
    song_id = db.Column(
        db.Integer, 
        db.ForeignKey("songs.id")
    )
    
    is_favorite = db.Column(db.Boolean, default=False)
    first_listened_at = db.Column(db.Date)
    
    created_at = db.Column(db.DateTime, default=lambda: now_jst)
    updated_at = db.Column(db.DateTime, default=lambda: now_jst, onupdate=lambda: now_jst)
    
    user = db.relationship(
        "User",
        back_populates = "user_songs", 
    )
    
    song = db.relationship(
        "Song", 
        back_populates = "user_songs"
    )


class UserArtist(db.Model):
    __tablename__ = "user_artists"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    user_id = db.Column(
        db.Integer, 
        db.ForeignKey("users.id"), 
    )
    
    artist_id = db.Column(
        db.Integer, 
        db.ForeignKey("artists.id"), 
    )
    
    created_at = db.Column(db.DateTime, default=lambda: now_jst)
    updated_at = db.Column(db.DateTime, default=lambda: now_jst, onupdate=lambda: now_jst)
    
    user = db.relationship(
        "User",
        back_populates = "user_artists", 
    )
    
    artist = db.relationship(
        "Artist", 
        back_populates = "user_artists"
    )


class UserPlaylist(db.Model):
    __tablename__ = "user_playlists"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    user_id = db.Column(
        db.Integer, 
        db.ForeignKey("users.id"), 
    )
    
    playlist_id = db.Column(
        db.Integer, 
        db.ForeignKey("playlists.id"), 
    )
    
    can_edit = db.Column(db.Boolean, default=True)
    is_library = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=lambda: now_jst)
    updated_at = db.Column(db.DateTime, default=lambda: now_jst, onupdate=lambda: now_jst)
    
    user = db.relationship(
        "User",
        back_populates = "user_artists", 
    )
    
    playlist = db.relationship(
        "Playlist", 
        back_populates = "user_playlists"
    )


# ============================================================================
# Imageモデル
# ============================================================================
class SongImage(db.Model):
    __tablename__ = "song_images"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    song_id = db.Column(
        db.Integer, 
        db.ForeignKey("songs.id"), 
    )
    
    song = db.relationship(
        "Song", 
        back_populates = "images"
    )

    path = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=lambda: now_jst)
    updated_at = db.Column(db.DateTime, default=lambda: now_jst, onupdate=lambda: now_jst)

class ArtistImage(db.Model):
    __tablename__ = "artist_images"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    artist_id = db.Column(
        db.Integer, 
        db.ForeignKey("artists.id"), 
    )
    artist = db.relationship(
        "Artist", 
        back_populates = "images"
    )

    path = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=lambda: now_jst)
    updated_at = db.Column(db.DateTime, default=lambda: now_jst, onupdate=lambda: now_jst)

class AlbumImage(db.Model):
    __tablename__ = "album_images"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    album_id = db.Column(
        db.Integer, 
        db.ForeignKey("albums.id"), 
    )
    album = db.relationship(
        "Album", 
        back_populates = "images"
    )
    
    path = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=lambda: now_jst)
    updated_at = db.Column(db.DateTime, default=lambda: now_jst, onupdate=lambda: now_jst)