
from .extensions import db
from .utils.converter import utc_now


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
    
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    
    
    composer_name = db.Column(db.String, nullable=True)
    has_lyrics = db.Column(db.Boolean, default=False)
    apple_music_url = db.Column(db.String, nullable=True)
    is_apple_digital_master = db.Column(db.Boolean, default=False)
    
    # catalogがないSongのための仮情報
    artist_name = db.Column(db.String, nullable=True)
    album_name = db.Column(db.String, nullable=True)
    
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
    
    song_playlists = db.relationship(
        "SongPlaylist",
        back_populates="song"
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
    
    song_images = db.relationship(
        "SongImage",
        back_populates = "song"
    )
    
    award_results_association = db.relationship(
        "AwardResultSong", 
        back_populates = "songs"
    )


class Artist(db.Model):
    __tablename__ = "artists"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    name_en = db.Column(db.String(255))
    
    apple_music_id = db.Column(db.String(20), unique=True, nullable=True)
    
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
        
    
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
    
    artist_images = db.relationship(
        "ArtistImage",
        back_populates = "artist"
    )
    
    award_results_association = db.relationship(
        "AwardResultArtist", 
        back_populates = "artists"
    )

class Album(db.Model):
    __tablename__ = "albums"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255))
    
    apple_music_id = db.Column(db.String(20), unique=True, nullable=True)
    
    is_compilation = db.Column(db.Boolean)
    is_single = db.Column(db.Boolean)
    release_date = db.Column(db.Date)
    
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    
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
    
    album_images = db.relationship(
        "AlbumImage",
        back_populates = "album"
    )


class Work(db.Model):
    __tablename__ = "works"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255))
    
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    
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
    
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    
    user_playlists = db.relationship(
        "UserPlaylist", 
        back_populates = "playlist", 
        cascade = "all, delete-orphan", 
    )
    
    song_playlists = db.relationship(
        "SongPlaylist", 
        back_populates = "playlist", 
        cascade = "all, delete-orphan", 
        order_by="SongPlaylist.position", 
    )
    
    playlist_images = db.relationship(
        "PlaylistImage", 
        back_populates = "playlist"
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
    
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    
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
        back_populates = "user", 
        cascade = "all, delete-orphan", 
    )
    
    awards = db.relationship(
        "Award", 
        back_populates = "user"
    )

# ============================================================================
# 中間テーブル
# ============================================================================

# Song と Artist の中間テーブル
class SongArtist(db.Model):
    __tablename__ = "song_artists"

    song_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "songs.id",
            ondelete="CASCADE",
            name="fk_song_artists_song_id_songs"
        ),
        primary_key=True
    )

    artist_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "artists.id",
            ondelete="CASCADE",
            name="fk_song_artists_artist_id_artists"
        ),
        primary_key=True
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
    created_at = db.Column(db.DateTime, default=utc_now)

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
    
    playlist = db.relationship(
        "Playlist",
        back_populates="song_playlists"
    )

    song = db.relationship(
        "Song",
        back_populates="song_playlists"
    )
    
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)


class PlaylistSnapshot(db.Model):
    __tablename__ = "playlist_snapshots"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    playlist_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "playlists.id",
            ondelete="CASCADE",
            name="fk_playlist_snapshots_playlist_id_playlists",
        ),
        nullable=False,
    )

    snapshot_date = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
    )

    created_at = db.Column(
        db.DateTime,
        default=utc_now,
        nullable=False,
    )


class PlaylistSnapshotSong(db.Model):
    __tablename__ = "playlist_snapshot_songs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    snapshot_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "playlist_snapshots.id",
            ondelete="CASCADE",
            name="fk_playlist_snapshot_songs_snapshot_id",
        ),
        nullable=False,
    )

    song_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "songs.id",
            ondelete="CASCADE",
            name="fk_playlist_snapshot_songs_song_id",
        ),
        nullable=False,
    )

    position = db.Column(db.Integer, nullable=True)

    created_at = db.Column(
        db.DateTime,
        default=utc_now,
        nullable=False,
    )

# ============================================================================
# 中間テーブル (User)
# ============================================================================

# UserとSongの関連を定義
class UserSong(db.Model):
    __tablename__ = "user_songs"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    user_id = db.Column(
        db.Integer, 
        db.ForeignKey("users.id", name="fk_user_songs_user_id_users")
    )
    
    song_id = db.Column(
        db.Integer, 
        db.ForeignKey("songs.id", name="fk_user_songs_song_id_songs")
    )
    
    apple_library_id = db.Column(db.String, nullable=True)
    
    is_favorite = db.Column(db.Boolean, default=False)
    first_listened_at = db.Column(db.Date)
    is_library = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    
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
        db.ForeignKey("users.id", name="fk_user_artists_user_id_users"), 
    )
    
    artist_id = db.Column(
        db.Integer, 
        db.ForeignKey("artists.id", name="fk_user_artists_artist_id_artists"), 
    )
    
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    
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
        db.ForeignKey("users.id", name="fk_user_playlists_user_id_users"), 
    )
    
    playlist_id = db.Column(
        db.Integer, 
        db.ForeignKey("playlists.id", name="fk_user_playlists_playlist_id_playlists"), 
    )
    
    can_edit = db.Column(db.Boolean, default=True)
    is_library = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    
    user = db.relationship(
        "User",
        back_populates = "user_playlists", 
    )
    
    playlist = db.relationship(
        "Playlist", 
        back_populates = "user_playlists"
    )


# ============================================================================
# Imageモデル
# ============================================================================
class Image(db.Model):
    __tablename__ = "images"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    path = db.Column(db.String, nullable=False)
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    
    source = db.Column(db.String, default="apple_music")
    
    bg_color = db.Column(db.String(6))
    text_color1 = db.Column(db.String(6))
    text_color2 = db.Column(db.String(6))
    text_color3 = db.Column(db.String(6))
    text_color4 = db.Column(db.String(6))
    
    song_images = db.relationship(
        "SongImage",
        back_populates = "image"
    )
    
    artist_images = db.relationship(
        "ArtistImage",
        back_populates = "image"
    )

    album_images = db.relationship(
        "AlbumImage",
        back_populates = "image"
    )
    
    playlist_images = db.relationship(
        "PlaylistImage",
        back_populates = "image"
    )
    
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    

class SongImage(db.Model):
    __tablename__ = "song_images"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    song_id = db.Column(
        db.Integer, 
        db.ForeignKey("songs.id", name="fk_song_images_song_id_songs"), 
    )
    song = db.relationship(
        "Song", 
        back_populates = "song_images"
    )

    image_id = db.Column(
        db.Integer,
        db.ForeignKey("images.id", name="fk_song_images_image_id_images"),
    )
    image = db.relationship(
        "Image",
        back_populates = "song_images"
    )
    
    is_main = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

class ArtistImage(db.Model):
    __tablename__ = "artist_images"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    artist_id = db.Column(
        db.Integer, 
        db.ForeignKey("artists.id", name="fk_artist_images_artist_id_artists"), 
    )
    artist = db.relationship(
        "Artist", 
        back_populates = "artist_images"
    )
    
    image_id = db.Column(
        db.Integer,
        db.ForeignKey("images.id", name="fk_artist_images_image_id_images"),
    )
    image = db.relationship(
        "Image",
        back_populates = "artist_images"
    )
    is_main = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)


class AlbumImage(db.Model):
    __tablename__ = "album_images"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    album_id = db.Column(
        db.Integer, 
        db.ForeignKey("albums.id", name="fk_album_images_album_id_albums"), 
    )
    album = db.relationship(
        "Album", 
        back_populates = "album_images"
    )
    
    image_id = db.Column(
        db.Integer,
        db.ForeignKey("images.id", name="fk_album_images_image_id_images"),
    )
    image = db.relationship(
        "Image",
        back_populates = "album_images"
    )
    
    is_main = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)


class PlaylistImage(db.Model):
    __tablename__ = "playlist_images"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    playlist_id = db.Column(
        db.Integer, 
        db.ForeignKey("playlists.id", name="fk_playlist_images_playlist_id_playlists"), 
    )
    playlist = db.relationship(
        "Playlist", 
        back_populates = "playlist_images"
    )
    
    image_id = db.Column(
        db.Integer,
        db.ForeignKey("images.id", name="fk_playlist_images_image_id_images"),
    )
    image = db.relationship(
        "Image",
        back_populates = "playlist_images"
    )
    
    is_main = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)


class Award(db.Model):
    __tablename__ = "awards"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 例: Grammy Awards, JAPAN MUSIC AWARDS
    name = db.Column(db.String(128), nullable=False, unique=True)

    country = db.Column(db.String(64))
    organization = db.Column(db.String(128))
    priority = db.Column(db.Integer)

    grid_columns_pc = db.Column(db.Integer, default=6)
    grid_columns_mobile = db.Column(db.Integer, default=3)
    
    user_id = db.Column(
        db.Integer, 
        db.ForeignKey(
            "users.id", 
            ondelete = "CASCADE", 
            name = "fk_award_user_id_users"
        ), 
        index = True, 
        nullable = False
    )
    
    user = db.relationship(
        "User", 
        back_populates = "awards"
    )

    created_at = db.Column(
        db.DateTime,
        default=utc_now
    )
    updated_at = db.Column(
        db.DateTime,
        default=utc_now,
        onupdate=utc_now
    )

    categories = db.relationship(
        "AwardCategory",
        back_populates="award",
        cascade="all, delete-orphan",
        passive_deletes=True
    )


class AwardCategory(db.Model):
    __tablename__ = "award_categories"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    award_id = db.Column(
        db.Integer,
        db.ForeignKey("awards.id", ondelete="CASCADE", name="fk_award_categories_award_id_awards"),
        index=True,
        nullable=False
    )

    # 実際の部門名
    # 例: 撮影賞, 撮影賞(カラー), 主演男優賞, 作品賞(コメディシリーズ)
    name = db.Column(db.String(128), nullable=False)

    # 必要なら別表示名
    display_name = db.Column(db.String(128))
    short_name = db.Column(db.String(32))

    # 賞内表示順
    award_order = db.Column(db.Integer)

    # 部門の存続情報（簡易版）
    start_year = db.Column(db.Integer)
    end_year = db.Column(db.Integer)
    history_note = db.Column(db.String(255))

    # 対象
    # song / artist / album / all
    subject_type = db.Column(db.String(32))

    # -------------------------
    # 表示用属性
    # -------------------------

    # 表示上まとめる親ラベル
    # 例: 撮影賞
    display_group_label = db.Column(db.String(128), index=True)

    # 表示上の枝ラベル
    # 例: カラー / 白黒 / コメディシリーズ / 単話
    display_variant_label = db.Column(db.String(64))

    # 「このカテゴリは親見出しの下に畳むか」
    display_as_child = db.Column(db.Boolean, default=False, index=True)

    created_at = db.Column(
        db.DateTime,
        default=utc_now
    )
    updated_at = db.Column(
        db.DateTime,
        default=utc_now,
        onupdate=utc_now
    )

    award = db.relationship("Award", back_populates="categories")

    results = db.relationship(
        "AwardResult",
        back_populates="award_category",
        cascade="all, delete-orphan",
        passive_deletes=True
    )


class AwardResult(db.Model):
    __tablename__ = "award_results"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    award_category_id = db.Column(
        db.Integer,
        db.ForeignKey("award_categories.id", ondelete="CASCADE", name="fk_award_results_award_category_id_award_categories"),
        index=True,
        nullable=False
    )

    # 年
    award_ceremony_id = db.Column(
        db.Integer, 
        db.ForeignKey(
            "award_ceremonies.id", 
            ondelete="CASCADE", 
            name="fk_award_results_award_ceremony_id_award_ceremonies"
        ), 
        index = True, 
    )

    # 受賞/候補
    # winner / nominee / shortlist など
    result_type = db.Column(db.String(32), index=True, nullable=False)
    won_flag = db.Column(db.Boolean, default=True)

    # 必要なら順位
    ranking = db.Column(db.Integer)

    # 特別賞など
    special = db.Column(db.Boolean, default=False)

    created_at = db.Column(
        db.DateTime,
        default=utc_now
    )
    updated_at = db.Column(
        db.DateTime,
        default=utc_now,
        onupdate=utc_now
    )

    award_category = db.relationship("AwardCategory", back_populates="results")
    award_ceremony = db.relationship("AwardCeremony", back_populates="results")

    artists_association = db.relationship(
        "AwardResultArtist",
        back_populates="award_result",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    artists = db.relationship(
        "Artist",
        secondary="award_result_artists",
        viewonly=True
    )

    songs_association = db.relationship(
        "AwardResultSong",
        back_populates="award_result",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    songs = db.relationship(
        "Song",
        secondary="award_result_songs",
        viewonly=True
    )

class AwardCeremony(db.Model):
    __tablename__ = "award_ceremonies"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    award_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "awards.id",
            ondelete="CASCADE",
            name="fk_award_ceremonies_award_id_awards"
        ),
        index=True,
        nullable=False
    )

    # 表示名
    # 例: "第96回", "2023-2024"
    display_name = db.Column(db.String(64), nullable=False)

    # 開催年
    # 例: 2024
    year = db.Column(db.Integer, index=True)

    # 開催日
    ceremony_date = db.Column(db.Date)

    results = db.relationship("AwardResult", back_populates="award_ceremony")

    created_at = db.Column(
        db.DateTime,
        default=utc_now
    )
    updated_at = db.Column(
        db.DateTime,
        default=utc_now,
        onupdate=utc_now
    )

class AwardResultArtist(db.Model):
    __tablename__ = "award_result_artists"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    award_result_id = db.Column(
        db.Integer,
        db.ForeignKey("award_results.id", ondelete="CASCADE", name="fk_award_result_artist_award_result_id_award_results"),
        index=True,
        nullable=False
    )

    artist_id = db.Column(
        db.Integer,
        db.ForeignKey("artists.id", ondelete="CASCADE", name="fk_award_result_artists_artist_id_artists"),
        index=True,
        nullable=False
    )

    display_order = db.Column(db.Integer)

    # 必要なら補足
    role_text = db.Column(db.String(64))

    created_at = db.Column(
        db.DateTime,
        default=utc_now
    )
    updated_at = db.Column(
        db.DateTime,
        default=utc_now,
        onupdate=utc_now
    )

    award_result = db.relationship("AwardResult", back_populates="artists_association")
    artists = db.relationship("Artist", back_populates="award_results_association")


class AwardResultSong(db.Model):
    __tablename__ = "award_result_songs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    award_result_id = db.Column(
        db.Integer,
        db.ForeignKey("award_results.id", ondelete="CASCADE", name="fk_award_result_songs_award_result_id_award_results"),
        index=True,
        nullable=False
    )

    song_id = db.Column(
        db.Integer,
        db.ForeignKey("songs.id", ondelete="CASCADE", name="fk_award_result_songs_song_id_songs"),
        index=True,
        nullable=False
    )

    display_order = db.Column(db.Integer, default=1)

    created_at = db.Column(
        db.DateTime,
        default=utc_now
    )
    updated_at = db.Column(
        db.DateTime,
        default=utc_now,
        onupdate=utc_now
    )

    award_result = db.relationship("AwardResult", back_populates="songs_association")
    songs = db.relationship("Song", back_populates="award_results_association")