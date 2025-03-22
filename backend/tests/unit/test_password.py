"""Unit tests for the password module."""

from taram.password import (
    hash_password,
    verify_password,
)


def test_verify_hashed_password(unique):
    """Hashing a plain password and verifying it should return true."""
    plain_password = unique("password")
    hashed_password = hash_password(plain_password)
    assert verify_password(plain_password, hashed_password)

def test_verify_wrong_password(unique):
    """Verifying a wrong password should return false."""
    plain_password1, plain_password2 = unique("password"), unique("password")
    hashed_password1 = hash_password(plain_password1)
    assert not verify_password(plain_password2, hashed_password1)
