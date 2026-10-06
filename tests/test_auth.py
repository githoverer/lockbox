from src.lockbox.auth import PasswordManager


def test_password_can_be_set_and_verified(tmp_path):

    path = tmp_path / "auth.json"

    manager = PasswordManager(path)

    manager.set_password("secret123")

    assert manager.is_configured()

    assert manager.verify_password(
        "secret123"
    )

    assert not manager.verify_password(
        "wrong-password"
    )


def test_password_hash_is_not_plaintext(tmp_path):

    path = tmp_path / "auth.json"

    manager = PasswordManager(path)

    manager.set_password("secret123")

    content = path.read_text(
        encoding="utf-8"
    )

    assert "secret123" not in content