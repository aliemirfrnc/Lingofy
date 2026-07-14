from cryptography.fernet import Fernet, InvalidToken

from backend.core.config import get_spotify_token_encryption_key

_PREFIX = "enc:v1:"

class TokenCipher:
    """Versioned at-rest encryption boundary for third-party OAuth tokens."""
    def __init__(self, key: bytes | None = None):
        self._fernet = Fernet(key or get_spotify_token_encryption_key())

    def encrypt(self, value: str) -> str:
        if not value:
            return value
        return _PREFIX + self._fernet.encrypt(value.encode("utf-8")).decode("ascii")

    def decrypt(self, value: str) -> tuple[str, bool]:
        """Return plaintext and whether a legacy plaintext record must be re-encrypted."""
        if not value or not value.startswith(_PREFIX):
            return value, bool(value)
        try:
            return self._fernet.decrypt(value[len(_PREFIX):].encode("ascii")).decode("utf-8"), False
        except InvalidToken as exc:
            raise ValueError("Stored Spotify token cannot be decrypted with the configured key") from exc

spotify_token_cipher = TokenCipher()
