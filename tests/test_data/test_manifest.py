import pytest

from misinfo.data.manifest import DataManifest, make_entry


def test_manifest_roundtrip(tmp_path) -> None:
    artefact = tmp_path / "artefact.txt"
    artefact.write_text("hello world")
    entry = make_entry("test@v0", artefact, preprocessing_version="1")
    manifest = DataManifest()
    manifest.add(entry)
    out = tmp_path / "manifest.json"
    manifest.write(out)
    loaded = DataManifest.read(out)
    assert loaded.entries == manifest.entries


def test_manifest_verify_detects_tamper(tmp_path) -> None:
    artefact = tmp_path / "artefact.txt"
    artefact.write_text("clean")
    manifest = DataManifest()
    manifest.add(make_entry("test@v0", artefact, preprocessing_version="1"))
    assert manifest.verify(repo_root=".") == []  # path is absolute via make_entry
    artefact.write_text("tampered")
    broken = manifest.verify(repo_root=".")
    assert broken == ["test@v0"]


def test_manifest_rejects_duplicate_id(tmp_path) -> None:
    artefact = tmp_path / "a.txt"
    artefact.write_text("x")
    m = DataManifest()
    m.add(make_entry("dup@v0", artefact, preprocessing_version="1"))
    with pytest.raises(ValueError):
        m.add(make_entry("dup@v0", artefact, preprocessing_version="1"))
