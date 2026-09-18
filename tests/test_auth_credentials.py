import pytest

from auth_credentials import (
    hash_password,
    verify_password,
    verify_admin_credentials,
)


def test_password_hash_is_not_plain_text():
    password = "Example-Test-Password-123!"

    stored_hash = hash_password(password)

    assert stored_hash != password
    assert stored_hash.startswith("pbkdf2_sha256$")


def test_same_password_produces_different_hashes():
    password = "Example-Test-Password-123!"

    first_hash = hash_password(password)
    second_hash = hash_password(password)

    assert first_hash != second_hash


def test_correct_password_is_accepted():
    password = "Example-Test-Password-123!"

    stored_hash = hash_password(password)

    assert verify_password(password, stored_hash) is True


def test_incorrect_password_is_rejected():
    stored_hash = hash_password(
        "Example-Test-Password-123!"
    )

    assert verify_password(
        "Incorrect-Password",
        stored_hash,
    ) is False


@pytest.mark.parametrize(
    "stored_hash",
    [
        "",
        "invalid",
        "pbkdf2_sha256$abc$salt$hash",
        "unknown$1000$00$00",
        "pbkdf2_sha256$999999999$00$00",
    ],
)
def test_malformed_hash_is_rejected(stored_hash):
    assert verify_password(
        "Example-Test-Password-123!",
        stored_hash,
    ) is False


def test_empty_password_cannot_be_hashed():
    with pytest.raises(ValueError):
        hash_password("")


def test_missing_admin_configuration_rejects_login(
    monkeypatch,
):
    monkeypatch.delenv(
        "ADMIN_USERNAME",
        raising=False,
    )

    monkeypatch.delenv(
        "ADMIN_PASSWORD_HASH",
        raising=False,
    )

    assert verify_admin_credentials(
        "admin",
        "Example-Test-Password-123!",
    ) is False


def test_valid_admin_credentials(monkeypatch):
    password = "Example-Test-Password-123!"

    monkeypatch.setenv(
        "ADMIN_USERNAME",
        "admin",
    )

    monkeypatch.setenv(
        "ADMIN_PASSWORD_HASH",
        hash_password(password),
    )

    assert verify_admin_credentials(
        "admin",
        password,
    ) is True


def test_invalid_admin_password(monkeypatch):
    monkeypatch.setenv(
        "ADMIN_USERNAME",
        "admin",
    )

    monkeypatch.setenv(
        "ADMIN_PASSWORD_HASH",
        hash_password(
            "Example-Test-Password-123!"
        ),
    )

    assert verify_admin_credentials(
        "admin",
        "Wrong-Password",
    ) is False


def test_invalid_admin_username(monkeypatch):
    password = "Example-Test-Password-123!"

    monkeypatch.setenv(
        "ADMIN_USERNAME",
        "admin",
    )

    monkeypatch.setenv(
        "ADMIN_PASSWORD_HASH",
        hash_password(password),
    )

    assert verify_admin_credentials(
        "another-user",
        password,
    ) is False