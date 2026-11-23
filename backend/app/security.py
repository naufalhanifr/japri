import hashlib
import secrets

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

MIN_PASSWORD_LENGTH = 12
MAX_PASSWORD_LENGTH = 1024

_hasher = PasswordHasher()
_dummy_hash = None


def hash_password(password):
    return _hasher.hash(password)


def verify_password(password_hash, password):
    try:
        return _hasher.verify(password_hash, password)
    except (VerificationError, InvalidHashError):
        return False


def verify_dummy(password):
    """Biaya hash yang sama untuk email tak dikenal, supaya waktu respons tidak membocorkan akun."""
    global _dummy_hash
    if _dummy_hash is None:
        _dummy_hash = _hasher.hash(secrets.token_urlsafe(16))
    verify_password(_dummy_hash, password)


def validate_new_password(password):
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Kata sandi minimal {MIN_PASSWORD_LENGTH} karakter.")
    if len(password) > MAX_PASSWORD_LENGTH:
        raise ValueError(f"Kata sandi maksimal {MAX_PASSWORD_LENGTH} karakter.")


def new_token():
    return secrets.token_urlsafe(32)


def hash_token(token):
    return hashlib.sha256(token.encode()).hexdigest()
