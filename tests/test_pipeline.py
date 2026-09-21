import shutil
import sqlite3
from decimal import Decimal
from pathlib import Path

from src.models import CSV_COLUMNS
from src.pipeline import run


def count(db_path: Path, query: str) -> int:
    with sqlite3.connect(db_path) as connection:
        return int(connection.execute(query).fetchone()[0])


def total_for(db_path: Path, table: str, column: str, key: str) -> Decimal:
    with sqlite3.connect(db_path) as connection:
        values = connection.execute(f"SELECT total FROM {table} WHERE {column} = ?", (key,))
        return sum((Decimal(value) for (value,) in values), Decimal(0))


def test_pipeline_inserts_expected_values(tmp_path: Path) -> None:
    db_path = tmp_path / "t.db"
    assert run(tmp_path / "in", db_path) == 0

    assert count(db_path, "SELECT COUNT(*) FROM transactions") == 15
    assert count(db_path, "SELECT COUNT(*) FROM processed_files") == 3
    assert count(db_path, "SELECT COUNT(*) FROM transactions WHERE est_suspecte = 1") == 5
    origin = "totals_sent_by_origin"
    assert total_for(db_path, origin, "iban_origine", "FR7611110000000000000000001") == Decimal("5850.60")
    assert total_for(db_path, origin, "iban_origine", "FR7633330000000000000000003") == Decimal("11210.25")


def test_rerun_creates_no_duplicates(tmp_path: Path) -> None:
    db_path = tmp_path / "t.db"
    input_dir = tmp_path / "in"
    assert run(input_dir, db_path) == 0
    shutil.copy(input_dir / "transactions_01.csv", input_dir / "copie.csv")
    assert run(input_dir, db_path) == 0
    assert count(db_path, "SELECT COUNT(*) FROM transactions") == 15
    assert count(db_path, "SELECT COUNT(*) FROM processed_files") == 3


def test_failure_returns_nonzero_and_leaves_clean_db(tmp_path: Path) -> None:
    db_path = tmp_path / "t.db"
    input_dir = tmp_path / "in"
    input_dir.mkdir()
    bad = ",".join(CSV_COLUMNS) + "\n"
    bad += "2026-01-01T10:00:00,FR1,France,Banque A,DE1,Allemagne,10.00,EUR\n"
    bad += "2026-01-01T11:00:00,FR1,France,Banque A,DE1,Allemagne,abc,EUR\n"
    (input_dir / "bad.csv").write_text(bad, encoding="utf-8")

    assert run(input_dir, db_path) == 1
    assert count(db_path, "SELECT COUNT(*) FROM transactions") == 15
    assert count(db_path, "SELECT COUNT(*) FROM processed_files WHERE original_name = 'bad.csv'") == 0

