import os


def get_session_secret() -> str:
    """
    Return the secret used to sign session cookies.

    Refuse to start if the secret is missing or too short.
    """

    secret = os.getenv("SESSION_SECRET_KEY")

    if not secret:
        raise RuntimeError(
            "SESSION_SECRET_KEY is not configured."
        )

    if len(secret) < 32:
        raise RuntimeError(
            "SESSION_SECRET_KEY must contain at least 32 characters."
        )

    return secret