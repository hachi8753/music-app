
from ..extensions import db
from ..models import Image, SongImage, PlaylistImage


def register_image(artwork):
    
    if artwork is None:
        return None
    
    path = artwork.get("url")

    if not path:
        return None

    image = (
        db.session.query(Image)
        .filter_by(path=path)
        .first()
    )

    if image:
        
        return image

    image = Image(
        path=path,
        width=artwork.get("width"),
        height=artwork.get("height"),
        bg_color=artwork.get("bgColor"),
        text_color1=artwork.get("textColor1"),
        text_color2=artwork.get("textColor2"),
        text_color3=artwork.get("textColor3"),
        text_color4=artwork.get("textColor4"),
    )
    db.session.add(image)
    db.session.flush()  # 追加: ここでIDを取得するためにflushを呼び出す

    return image


def register_song_image(song, image):
    if not image:
        return None

    song_image = (
        db.session.query(SongImage)
        .filter_by(song_id=song.id, image_id=image.id)
        .first()
    )

    if song_image:
        return song_image

    song_image = SongImage(song_id=song.id, image_id=image.id)
    db.session.add(song_image)
    db.session.flush()  # 追加: ここでIDを取得するためにflushを呼び出す

    return song_image


def register_playlist_image(playlist, image):
    if not image:
        return None

    playlist_image = (
        db.session.query(PlaylistImage)
        .filter_by(playlist_id=playlist.id, image_id=image.id)
        .first()
    )

    if playlist_image:
        return playlist_image

    playlist_image = PlaylistImage(playlist_id=playlist.id, image_id=image.id)
    db.session.add(playlist_image)
    db.session.flush()  # 追加: ここでIDを取得するためにflushを呼び出す

    return playlist_image