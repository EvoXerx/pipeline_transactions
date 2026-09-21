from decimal import Decimal
from pathlib import Path

import pytest

from src.loader import load_csv
from src.models import CSV_COLUMNS

HEADER = ",".join(CSV_COLUMNS)
GOOD = "2026-01-01T10:00:00,FR1,France,Banque A,DE1,Allemagne,47.90,EUR"


def write(tmp_path: Path, *lines: str) -> Path:
    path = tmp_path / "t.csv"
    path.write_text("\n".join([HEADER, *lines]) + "\n", encoding="utf-8")
    return path


def test_load_valid_file(tmp_path: Path) -> None:
    transactions = load_csv(write(tmp_path, GOOD))
    assert transactions[0]["montant"] == Decimal("47.90")


@pytest.mark.parametrize(
    "bad_line",
    [
        "2026-01-01T10:00:00,FR1,France,Banque A,DE1,Allemagne,abc,EUR",
        "pas-une-date,FR1,France,Banque A,DE1,Allemagne,47.90,EUR",
        "2026-01-01T10:00:00,FR1,France,Banque A",
    ],
)
def test_invalid_row_rejects_whole_file(tmp_path: Path, bad_line: str) -> None:
    with pytest.raises(ValueError, match="ligne 3"):
        load_csv(write(tmp_path, GOOD, bad_line))
