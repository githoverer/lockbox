import hashlib
import json
import secrets
from pathlib import Path


class PasswordManager:

    def __init__(self, path: str | Path):

        self.path = Path(path)

    def _hash_password(
        self,
        password: str,
        salt: str,
    ) -> str:

        return hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            200_000,
        ).hex()

    def is_configured(self) -> bool:

        return self.path.exists()

    def set_password(
        self,
        password: str,
    ) -> None:

        salt = secrets.token_hex(16)

        password_hash = self._hash_password(
            password,
            salt,
        )

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        data = {
            "salt": salt,
            "password_hash": password_hash,
        }

        self.path.write_text(
            json.dumps(
                data,
                indent=4,
            ),
            encoding="utf-8",
        )

    def verify_password(
        self,
        password: str,
    ) -> bool:

        if not self.path.exists():
            return False

        data = json.loads(
            self.path.read_text(
                encoding="utf-8"
            )
        )

        salt = data["salt"]

        expected_hash = data[
            "password_hash"
        ]

        actual_hash = self._hash_password(
            password,
            salt,
        )

        return secrets.compare_digest(
            actual_hash,
            expected_hash,
        )