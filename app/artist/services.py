
from ..extensions import db
from ..models import Artist


def register_artist(data) -> Artist:
    attributes = data.get("attributes")
    # ArtistのCatalog Id
    apple_music_id = data.get("id")
    name = attributes.get("name")
    
    artist = db.session.query(Artist).filter_by(apple_music_id=apple_music_id).first()
    
    if artist:
        # 既存のArtistを更新
        if name:
            artist.name = name
        
    else:
        # 新しいArtistを作成
        artist = Artist(
            apple_music_id=apple_music_id,
            name=name,
        )
        db.session.add(artist)
    
    db.session.flush()
    
    return artist