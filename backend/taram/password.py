"""Password functions."""

import re

import bcrypt


class InvalidPassword(Exception):
    """Raised when an invalid password is given."""


def validate_passwords(password1: str, password2: str) -> None:
    """Validate that two passwords are the same and respect the policy."""
    if not password1 or not password2:
        raise InvalidPassword("Empty password")

    if password1 != password2:
        raise InvalidPassword("Passwords do not match")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify whether the plain password matches the hashed password."""
    if m := re.match(r"{(?P<scheme>.*?)}(?P<hashed_password>.*)", hashed_password):
        match m.group("scheme"):
            case "BLF-CRYPT":
                return bcrypt.checkpw(
                    plain_password.encode("utf-8"),
                    m.group("hashed_password").encode("utf-8"),
                )
            case scheme:
                raise ValueError(f"Unsupported scheme: {scheme}")

    raise ValueError(f"Missing scheme: {hashed_password}")


def hash_password(plain_password: str, scheme="BLF-CRYPT") -> str:
    """Return a hashed password from a plain password."""
    match scheme:
        case "BLF-CRYPT":
            hashed_password = bcrypt.hashpw(
                plain_password.encode("utf-8"),
                bcrypt.gensalt(),
            ).decode("utf-8")
        case _:
            raise ValueError(f"Unsupported scheme: {scheme}")

    return f"{{{scheme}}}{hashed_password}"
