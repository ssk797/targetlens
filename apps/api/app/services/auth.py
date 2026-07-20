"""Small, dependency-free helpers for local TargetLens authentication.

Passwords are never stored in clear text.  Session cookies contain an
opaque random token; only its SHA-256 digest is persisted, so a database
dump cannot be replayed as a logged-in browser session.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import re
import secrets


PASSWORD_SCHEME = "scrypt"
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def normalize_email(value: str) -> str:
    return value.strip().lower()


def is_valid_email(value: str) -> bool:
    return bool(EMAIL_PATTERN.fullmatch(normalize_email(value)))


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1)
    encode = lambda data: base64.urlsafe_b64encode(data).decode("ascii")
    return f"{PASSWORD_SCHEME}$16384$8$1${encode(salt)}${encode(digest)}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        scheme, n_value, r_value, p_value, salt_value, digest_value = encoded.split("$")
        if scheme != PASSWORD_SCHEME:
            return False
        salt = base64.urlsafe_b64decode(salt_value.encode("ascii"))
        expected = base64.urlsafe_b64decode(digest_value.encode("ascii"))
        actual = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=int(n_value), r=int(r_value), p=int(p_value))
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def new_session_token() -> str:
    return secrets.token_urlsafe(32)


def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
