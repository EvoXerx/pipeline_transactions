import csv
import hashlib
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from src.models import CSV_COLUMNS, LoadedFile, Transaction


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _parse_row(row: dict[str, str], line: int) -> Transaction:
    missing = [column for column in CSV_COLUMNS if not row.get(column)]
    if missing:
        raise ValueError(f"ligne {line} : colonne(s) manquante(s) {missing}")
    try:
        datetime.fromisoformat(row["datetime_transaction"])
    except ValueError:
        raise ValueError(f"ligne {line} : date illisible") from None
    try:
        montant = Decimal(row["montant"])
    except InvalidOperation:
        raise ValueError(f"ligne {line} : montant non numérique") from None
    return Transaction(
        datetime_transaction=row["datetime_transaction"],
        iban_origine=row["iban_origine"],
        pays_source=row["pays_source"],
        banque_source=row["banque_source"],
        iban_destinataire=row["iban_destinataire"],
        pays_destinataire=row["pays_destinataire"],
        montant=montant,
        devise=row["devise"],
    )


def load_csv(path: Path) -> list[Transaction]:
    with path.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        return [_parse_row(row, line) for line, row in enumerate(reader, start=2)]


def load_file(path: Path) -> LoadedFile:
    return {
        "path": str(path),
        "content_hash": file_sha256(path),
        "transactions": load_csv(path),
    }
