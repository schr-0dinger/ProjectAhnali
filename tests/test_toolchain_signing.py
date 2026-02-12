import zipfile
from pathlib import Path

import pytest

from apk.toolchain import (
    _resolve_signing_params,
    _verify_reproducible_archive,
    _zip_content_digest,
)


def _write_zip(path: Path, entries: dict[str, bytes]):
    with zipfile.ZipFile(path, "w") as zf:
        for name, data in entries.items():
            zf.writestr(name, data)


def test_resolve_signing_params_debug_defaults(tmp_path):
    ks, alias, store_pass, key_pass, ensure_debug = _resolve_signing_params(
        out_dir=tmp_path,
        signing_mode="debug",
    )
    assert ks == tmp_path / "debug.keystore"
    assert alias == "androiddebugkey"
    assert store_pass == "android"
    assert key_pass == "android"
    assert ensure_debug is True


def test_resolve_signing_params_release_requires_keystore_and_pass(tmp_path):
    with pytest.raises(RuntimeError, match="keystore_path"):
        _resolve_signing_params(
            out_dir=tmp_path,
            signing_mode="release",
            keystore_pass="secret",
        )
    with pytest.raises(RuntimeError, match="keystore_pass"):
        _resolve_signing_params(
            out_dir=tmp_path,
            signing_mode="release",
            keystore_path=tmp_path / "release.jks",
        )


def test_resolve_signing_params_release_defaults_key_pass(tmp_path):
    ks, alias, store_pass, key_pass, ensure_debug = _resolve_signing_params(
        out_dir=tmp_path,
        signing_mode="release",
        keystore_path=tmp_path / "release.jks",
        keystore_alias="release_alias",
        keystore_pass="secret",
        key_pass=None,
    )
    assert ks == tmp_path / "release.jks"
    assert alias == "release_alias"
    assert store_pass == "secret"
    assert key_pass == "secret"
    assert ensure_debug is False


def test_verify_reproducible_archive_detects_changes(tmp_path):
    digest_file = tmp_path / "unsigned.apk.sha256"
    zip_a = tmp_path / "a.zip"
    zip_b = tmp_path / "b.zip"
    zip_c = tmp_path / "c.zip"

    _write_zip(zip_a, {"classes.dex": b"abc", "res/raw/x.txt": b"1"})
    _write_zip(zip_b, {"res/raw/x.txt": b"1", "classes.dex": b"abc"})
    _write_zip(zip_c, {"classes.dex": b"changed", "res/raw/x.txt": b"1"})

    first = _verify_reproducible_archive(zip_a, digest_file)
    second = _verify_reproducible_archive(zip_b, digest_file)
    assert first == second
    assert _zip_content_digest(zip_a) == _zip_content_digest(zip_b)

    with pytest.raises(RuntimeError, match="Reproducibility check failed"):
        _verify_reproducible_archive(zip_c, digest_file)
