
from ..extensions import db
from ..models import Album

def register_album(data) -> Album:
    attributes = data.get("attributes")
    # AlbumのCatalog Id
    apple_music_id = data.get("id")
    
    title = attributes.get("name")
    
    album = db.session.query(Album).filter_by(apple_music_id=apple_music_id).first()
    
    if album:
        # 既存のAlbumを更新
        if title:
            album.title = title
        
    else:
        # 新しいAlbumを作成
        album = Album(
            apple_music_id=apple_music_id,
            title=title,
        )
        db.session.add(album)
    
    db.session.flush()
    
    return album