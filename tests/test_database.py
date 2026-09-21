import sqlite3
from decimal import Decimal
from pathlib import Path

import pytest

from src import database
from src.database import insert_file, insert_with_retry
from src.models import LoadedFile
from tests.test_processing import make


def loaded_file(name: str = "a.csv", content_hash: str = "h1") -> LoadedFile:
    return {
        "path": name,
        "content_hash": content_hash,
        "transactions": [make("FR-A", "Banque A", "FR-X", "83.25")],
    }


def count(db_path: Path, table: str) -> int:
    with sqlite3.connect(db_path) as connection:
        return int(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])


def test_insert_is_all_or_nothing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db_path = tmp_path / "t.db"

    def boom(_: object) -> dict[str, Decimal]:
        raise RuntimeError("panne en cours d'insertion")

    monkeypatch.setattr(database, "sum_sent_by_bank", boom)
    with pytest.raises(RuntimeError):
        insert_file(db_path, loaded_file())
    assert count(db_path, "transactions") == 0
    assert count(db_path, "processed_files") == 0


def test_same_content_under_another_name_is_skipped(tmp_path: Path) -> None:
    db_path = tmp_path / "t.db"
    assert insert_file(db_path, loaded_file("a.csv")) is True
    assert insert_file(db_path, loaded_file("copie.csv")) is False
    assert count(db_path, "transactions") == 1


def test_no_retry_on_integrity_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[int] = []

    def broken(db_path: Path, loaded: LoadedFile) -> bool:
        calls.append(1)
        raise sqlite3.IntegrityError("UNIQUE constraint failed")

    monkeypatch.setattr(database, "insert_file", broken)
    with pytest.raises(sqlite3.IntegrityError):
        insert_with_retry(tmp_path / "t.db", loaded_file(), delay=0)
    assert len(calls) == 1


def test_retry_on_locked_database(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[int] = []

    def flaky(db_path: Path, loaded: LoadedFile) -> bool:
        calls.append(1)
        if len(calls) == 1:
            raise sqlite3.OperationalError("database is locked")
        return True

    monkeypatch.setattr(database, "insert_file", flaky)
    assert insert_with_retry(tmp_path / "t.db", loaded_file(), delay=0) is True
    assert len(calls) == 2
