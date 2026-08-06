import os

from cryptography.fernet import Fernet


def _get_fernet() -> Fernet:

    key = os.getenv(
        "STORE_CREDENTIAL_ENCRYPTION_KEY"
    )

    if not key:
        raise RuntimeError(
            "STORE_CREDENTIAL_ENCRYPTION_KEY is not configured"
        )

    return Fernet(
        key.encode()
    )


def encrypt_store_password(
    password: str
) -> str:

    return (
        _get_fernet()
        .encrypt(password.encode())
        .decode()
    )


def decrypt_store_password(
    encrypted_password: str
) -> str:

    return (
        _get_fernet()
        .decrypt(
            encrypted_password.encode()
        )
        .decode()
    )