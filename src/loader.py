import csv
import hashlib
from pathlib import Path
from typing import cast

from src.models import LoadedFile, Transaction


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_csv(path: Path) -> list[Transaction]:
    with path.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        return [cast(Transaction, dict(row)) for row in reader]


def load_file(path: Path) -> LoadedFile:
    return {
        "path": str(path),
        "content_hash": file_sha256(path),
        "transactions": load_csv(path),
    }

