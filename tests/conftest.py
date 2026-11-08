import pytest

from src.infrastructure import storage as storage_module
from src.infrastructure.storage import NoteStorage


@pytest.fixture
def storage(tmp_path):
    return NoteStorage(tmp_path / "notes.json")


@pytest.fixture
def failed_replace(monkeypatch):
    def deny_replace():
        def fail(*args):
            raise OSError("Имитация сбоя до замены файла")

        monkeypatch.setattr(storage_module.os, "replace", fail)

    return deny_replace
