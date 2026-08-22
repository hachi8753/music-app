import requests

developer_token = "ここにDeveloper Token"

url = "https://api.music.apple.com/v1/catalog/jp/search"

headers = {
    "Authorization": f"Bearer {developer_token}"
}

params = {
    "term": "The Beatles",
    "types": "songs"
}

response = requests.get(
    url,
    headers=headers,
    params=params
)

print(response.status_code)
print(response.json())