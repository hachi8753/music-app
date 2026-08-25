import time
import jwt
import os
from dotenv import load_dotenv

load_dotenv()

team_id = os.getenv("APPLE_TEAM_ID")
key_id = os.getenv("APPLE_KEY_ID")
private_key_path = os.getenv("APPLE_PRIVATE_KEY_PATH")


print(team_id)
print(key_id)
print(private_key_path)

with open(private_key_path, "r") as f:
    private_key = f.read()

headers = {
    "alg": "ES256",
    "kid": key_id,
}

payload = {
    "iss": team_id,
    "iat": int(time.time()),
    "exp": int(time.time()) + 15777000,
}

token = jwt.encode(
    payload,
    private_key,
    algorithm="ES256",
    headers=headers,
)

print(token)