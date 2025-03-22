"""Password functions."""

import bcrypt


class InvalidPassword(Exception):
    """Raised when an invalid password is given."""


def verify_password(plain_password, hashed_password):
    """Verify whether the plain password matches the hashed password."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def validate_passwords(password1, password2):
    """Validate that two passwords are the same and respect the policy."""
    if not password1 or not password2:
        raise InvalidPassword("Empty password")

    if password1 != password2:
        raise InvalidPassword("Passwords do not match")


def hash_password(plain_password):
    """Return a hashed password from a plain password."""
    return bcrypt.hashpw(
        plain_password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")
