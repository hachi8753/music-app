

def get_image_path(image, width, height):
    return (
        image.path
        .replace("{w}", str(width))
        .replace("{h}", str(height))
    )


def get_main_image_path_of_song(song, width, height):
    tmp_path = ""
    for song_image in song.song_images:
        if song_image.is_main:
            return get_image_path(song_image.image, width, height)
        else:
            tmp_path = get_image_path(song_image.image, width, height)
    if tmp_path: # 仮でis_main=Falseのimageを返す
        return tmp_path
    else:
        return None