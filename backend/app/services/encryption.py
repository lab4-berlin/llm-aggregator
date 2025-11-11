from cryptography.fernet import Fernet
from app.config import settings
import base64
import hashlib


def get_encryption_key() -> bytes:
    """Convert the encryption key from settings to Fernet-compatible format."""
    key = settings.ENCRYPTION_KEY.encode()
    # Hash the key to get exactly 32 bytes
    key_hash = hashlib.sha256(key).digest()
    # Encode to base64 for Fernet
    return base64.urlsafe_b64encode(key_hash)


def encrypt_api_key(api_key: str) -> str:
    """Encrypt an API key."""
    f = Fernet(get_encryption_key())
    encrypted = f.encrypt(api_key.encode())
    return encrypted.decode()


def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt an API key."""
    f = Fernet(get_encryption_key())
    decrypted = f.decrypt(encrypted_key.encode())
    return decrypted.decode()

