import os

from cryptography.fernet import Fernet


def get_cipher():
    key = os.getenv("TOKEN_ENCRYPTION_KEY")

    if not key:
        raise RuntimeError("TOKEN_ENCRYPTION_KEY is not configured")

    return Fernet(key.encode())


def encrypt_token(token):
    cipher = get_cipher()
    return cipher.encrypt(token.encode()).decode()


def decrypt_token(encrypted_token):
    cipher = get_cipher()
    return cipher.decrypt(encrypted_token.encode()).decode()