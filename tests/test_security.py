"""Week 6: Security audit tests."""

import os
import tempfile
from pathlib import Path

from gli_flow.security.file_protection import (
    secure_run_directory,
    encrypt_file_aes256,
    decrypt_file_aes256,
)


def test_secure_run_directory_sets_permissions():
    with tempfile.TemporaryDirectory() as tmp:
        secure_run_directory(Path(tmp), user_id="test_user")
        mode = os.stat(tmp).st_mode & 0o777
        assert mode <= 0o700


def test_encrypt_decrypt_roundtrip():
    with tempfile.TemporaryDirectory() as tmp:
        key = b"k" * 32
        original = "sensitive data: GDS path = /secret"
        input_file = Path(tmp) / "input.txt"
        output_file = Path(tmp) / "output.txt"
        input_file.write_text(original)

        encrypted = encrypt_file_aes256(input_file, key=key)
        assert encrypted.exists()

        decrypted = decrypt_file_aes256(encrypted, key=key, output_path=output_file)
        assert decrypted.read_text() == original


def test_encrypt_wrong_key_fails():
    with tempfile.TemporaryDirectory() as tmp:
        key = b"k" * 32
        wrong_key = b"w" * 32
        input_file = Path(tmp) / "input.txt"
        output_file = Path(tmp) / "output.txt"
        input_file.write_text("test data")
        encrypted = encrypt_file_aes256(input_file, key=key)
        assert encrypted.exists()
        try:
            decrypt_file_aes256(encrypted, key=wrong_key, output_path=output_file)
            assert False, "Should have raised"
        except Exception:
            pass
