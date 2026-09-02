import os

import time
import requests
from dotenv import load_dotenv
from pprint import pprint
from ..utils.encryption import decrypt_token

load_dotenv()

BASE_URL = "https://api.music.apple.com"
CATALOG_FETCH_LIMIT = 100
ISRC_FETCH_LIMIT = 25

def get_developer_token():
    return os.getenv("APPLE_MUSIC_DEVELOPER_TOKEN")


def get_headers():
    developer_token = get_developer_token()
    return {
        "Authorization": f"Bearer {developer_token}",
    }


def get_user_headers(user):
    
    developer_token = get_developer_token()
    
    encrypted_token = user.apple_music_user_token
    user_token = decrypt_token(encrypted_token)
    
    return {
        "Authorization": f"Bearer {developer_token}", 
        "Music-User-Token": user_token,
    }

    
def _get(url, params=None):

    response = requests.get(
        url,
        headers=get_headers(),
        params=params,
    )

    response.raise_for_status()

    return response.json()


def chunks(items, size):

    for i in range(0, len(items), size):

        yield items[i:i + size]


def request_with_retry(url, params=None, max_retries=3):
    
    for attempt in range(max_retries):
        
        response = requests.get(
            url, 
            headers = get_headers(), 
            params = params, 
        )
        
        if response.status_code != 429:
            response.raise_for_status()
            return response.json()
        
        # Rate Limit
        wait_seconds = 2 ** attempt
        
        time.sleep(wait_seconds)
    
    response.raise_for_status()


def get_songs(song_catalog_ids):
    
    results = []
        
    for ids in chunks(song_catalog_ids, CATALOG_FETCH_LIMIT):
        
        url = f'{BASE_URL}/v1/catalog/jp/songs'
        params = {
            "ids": ",".join(map(str, ids))
        }
        
        result = _get(url, params)
        results.extend(result["data"])
    
    return results


def get_albums(album_catalog_ids):
    
    results = []
    
    for ids in chunks(album_catalog_ids, CATALOG_FETCH_LIMIT):
        
        url = f'{BASE_URL}/v1/catalog/jp/albums'
        params = {
            "ids": ",".join(map(str, ids))
        }
        
        result = _get(url, params)
        results.extend(result["data"])
    
    return results


def get_all_playlists(user):
    
    results = []
    limit = 50
    
    headers = get_user_headers(user)
    
    url = f"{BASE_URL}/v1/me/library/playlists"
    
    while True:
        print(url)
        response = requests.get(
            url,
            headers=headers,
            params={
                "limit": limit,
            }
        )
        response.raise_for_status()
        result = response.json()

        results.extend(result["data"])
        
        if "next" not in result:
            break
        url = f"{BASE_URL}{result["next"]}"
        
    
    return results


def get_all_playlist_songs(user, playlist):
    
    results = []
    limit = 50
    
    headers = get_user_headers(user)
    apple_music_id = playlist.apple_music_id
    
    url = f"{BASE_URL}/v1/me/library/playlists/{apple_music_id}/tracks"
    # url = f"{BASE_URL}/v1/me/library/playlists/p.PkxVB2VUPr6VAzY/tracks
    
    while True:
        print(url)
        response = requests.get(
            url,
            headers=headers,
            params={
                "limit": limit,
            }
        )
        response.raise_for_status()
        result = response.json()

        results.extend(result["data"])
        
        if "next" not in result:
            break
        url = f"{BASE_URL}{result["next"]}"
        
    
    return results