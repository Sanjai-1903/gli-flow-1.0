"""
File protection for user design IP.
Implements encryption at rest and access control.
"""

import os
import stat
import hashlib
import secrets
import logging
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)


def secure_run_directory(run_dir: Path, user_id: str) -> None:
    """Set strict permissions on run directory."""
    try:
        run_dir.chmod(0o700)
        for item in run_dir.rglob("*"):
            if item.is_file():
                item.chmod(0o600)
            elif item.is_dir():
                item.chmod(0o700)
    except Exception as e:
        log.warning(f"Could not set permissions on {run_dir}: {e}")


def encrypt_file_aes256(file_path: Path, key: bytes) -> Path:
    """Encrypt a file with AES-256-GCM."""
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    except ImportError:
        log.warning("cryptography package not installed. RTL files stored without encryption. Install: pip install cryptography")
        return file_path

    aesgcm = AESGCM(key)
    nonce = secrets.token_bytes(12)

    plaintext = file_path.read_bytes()
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)

    enc_path = file_path.with_suffix(file_path.suffix + ".enc")
    enc_path.write_bytes(nonce + ciphertext)

    _secure_delete(file_path)

    return enc_path


def decrypt_file_aes256(enc_path: Path, key: bytes, output_path: Path) -> Path:
    """Decrypt an AES-256-GCM encrypted file."""
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    aesgcm = AESGCM(key)
    data = enc_path.read_bytes()
    nonce = data[:12]
    ciphertext = data[12:]

    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    output_path.write_bytes(plaintext)
    return output_path


def _secure_delete(file_path: Path) -> None:
    """Overwrite file with zeros before deletion."""
    try:
        size = file_path.stat().st_size
        with open(file_path, "r+b") as f:
            f.write(b"\x00" * size)
        file_path.unlink()
    except Exception:
        file_path.unlink(missing_ok=True)


def get_or_create_user_key(user_id: str) -> bytes:
    """Get or create encryption key for a user."""
    kms_key_id = os.environ.get("GLI_KMS_KEY_ID")
    if kms_key_id:
        return _get_kms_key(kms_key_id, user_id)

    secret = os.environ.get("GLI_ENCRYPTION_SECRET")
    if not secret:
        raise RuntimeError("GLI_ENCRYPTION_SECRET environment variable is not set. Set it to a 32-byte hex key for production use.")

    key_material = f"{secret}:{user_id}".encode()
    return hashlib.sha256(key_material).digest()


def _get_kms_key(kms_key_id: str, user_id: str) -> bytes:
    """Get data key from AWS KMS."""
    try:
        import boto3
        kms = boto3.client("kms")
        response = kms.generate_data_key(
            KeyId=kms_key_id, KeySpec="AES_256", EncryptionContext={"user_id": user_id}
        )
        return response["Plaintext"]
    except Exception as e:
        log.error(f"KMS key retrieval failed: {e}")
        raise
