import hashlib
import hmac
import os
import secrets


ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 600_000
SALT_BYTES = 16


def hash_password(password: str) -> str:
    """
    Hash an administrator password using PBKDF2-HMAC-SHA256.

    A random salt is generated for each password.
    """

    if not isinstance(password, str) or not password:
        raise ValueError("Password must not be empty.")

    salt = secrets.token_bytes(SALT_BYTES)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        ITERATIONS,
    )

    return (
        f"{ALGORITHM}$"
        f"{ITERATIONS}$"
        f"{salt.hex()}$"
        f"{password_hash.hex()}"
    )


def verify_password(
    password: str,
    stored_hash: str,
) -> bool:
    """
    Verify a password against a stored PBKDF2 hash.

    Return False for invalid or malformed hashes.
    """

    if not isinstance(password, str):
        return False

    if not isinstance(stored_hash, str):
        return False

    try:
        algorithm, iterations_text, salt_hex, hash_hex = (
            stored_hash.split("$")
        )

        if algorithm != ALGORITHM:
            return False

        iterations = int(iterations_text)

        if iterations < 1 or iterations > ITERATIONS:
            return False

        salt = bytes.fromhex(salt_hex)
        expected_hash = bytes.fromhex(hash_hex)

        if len(salt) != SALT_BYTES:
            return False

        if len(expected_hash) != hashlib.sha256().digest_size:
            return False

        calculated_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            iterations,
        )

        return hmac.compare_digest(
            calculated_hash,
            expected_hash,
        )

    except (ValueError, TypeError):
        return False


def verify_admin_credentials(
    username: str,
    password: str,
) -> bool:
    """
    Verify credentials against environment configuration.

    Missing configuration must never permit login.
    """

    configured_username = os.getenv("ADMIN_USERNAME")
    configured_password_hash = os.getenv("ADMIN_PASSWORD_HASH")

    if not configured_username or not configured_password_hash:
        return False

    if not isinstance(username, str):
        return False

    if not hmac.compare_digest(
        username.encode("utf-8"),
        configured_username.encode("utf-8"),
    ):
        return False

    return verify_password(
        password,
        configured_password_hash,
    )