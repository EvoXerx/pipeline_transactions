import sqlite3
import time
from pathlib import Path

from src.models import LoadedFile
from src.processing import (
    flag_transactions,
    sum_received_by_iban,
    sum_sent_by_bank,
    sum_sent_by_origin,
)


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS processed_files (
    content_hash TEXT PRIMARY KEY,
    original_name TEXT NOT NULL,
    processed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_hash TEXT NOT NULL,
    datetime_transaction TEXT NOT NULL,
    iban_origine TEXT NOT NULL,
    pays_source TEXT NOT NULL,
    banque_source TEXT NOT NULL,
    iban_destinataire TEXT NOT NULL,
    pays_destinataire TEXT NOT NULL,
    montant TEXT NOT NULL,
    devise TEXT NOT NULL,
    est_suspecte INTEGER NOT NULL CHECK (est_suspecte IN (0, 1)),
    FOREIGN KEY (content_hash) REFERENCES processed_files(content_hash)
);

CREATE TABLE IF NOT EXISTS totals_sent_by_origin (
    content_hash TEXT NOT NULL,
    iban_origine TEXT NOT NULL,
    total TEXT NOT NULL,
    PRIMARY KEY (content_hash, iban_origine),
    FOREIGN KEY (content_hash) REFERENCES processed_files(content_hash)
);

CREATE TABLE IF NOT EXISTS totals_sent_by_bank (
    content_hash TEXT NOT NULL,
    banque_source TEXT NOT NULL,
    total TEXT NOT NULL,
    PRIMARY KEY (content_hash, banque_source),
    FOREIGN KEY (content_hash) REFERENCES processed_files(content_hash)
);

CREATE TABLE IF NOT EXISTS totals_received_by_iban (
    content_hash TEXT NOT NULL,
    iban_destinataire TEXT NOT NULL,
    total TEXT NOT NULL,
    PRIMARY KEY (content_hash, iban_destinataire),
    FOREIGN KEY (content_hash) REFERENCES processed_files(content_hash)
);
"""


def setup_database(connection: sqlite3.Connection) -> None:
    connection.executescript(SCHEMA)


def _insert_loaded_file(connection: sqlite3.Connection, loaded: LoadedFile) -> bool:
    content_hash = loaded["content_hash"]
    cursor = connection.execute(
        "INSERT OR IGNORE INTO processed_files(content_hash, original_name) VALUES (?, ?)",
        (content_hash, Path(loaded["path"]).name),
    )
    if cursor.rowcount == 0:
        return False

    transactions = loaded["transactions"]
    connection.executemany(
        """
        INSERT INTO transactions(
            content_hash, datetime_transaction, iban_origine,
            pays_source, banque_source, iban_destinataire, pays_destinataire,
            montant, devise, est_suspecte
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                content_hash,
                t["datetime_transaction"],
                t["iban_origine"],
                t["pays_source"],
                t["banque_source"],
                t["iban_destinataire"],
                t["pays_destinataire"],
                str(t["montant"]),
                t["devise"],
                int(t["est_suspecte"]),
            )
            for t in flag_transactions(transactions)
        ],
    )

    totals = {
        "totals_sent_by_origin": sum_sent_by_origin(transactions),
        "totals_sent_by_bank": sum_sent_by_bank(transactions),
        "totals_received_by_iban": sum_received_by_iban(transactions),
    }
    for table, values in totals.items():
        connection.executemany(
            f"INSERT INTO {table} VALUES (?, ?, ?)",
            [(content_hash, key, str(total)) for key, total in values.items()],
        )
    return True


def insert_file(db_path: Path, loaded: LoadedFile) -> bool:
    connection = sqlite3.connect(db_path)
    try:
        setup_database(connection)
        with connection:
            return _insert_loaded_file(connection, loaded)
    finally:
        connection.close()


def insert_with_retry(
    db_path: Path, loaded: LoadedFile, attempts: int = 3, delay: float = 0.5
) -> bool:
    for _ in range(attempts - 1):
        try:
            return insert_file(db_path, loaded)
        except sqlite3.OperationalError:
            time.sleep(delay)
    return insert_file(db_path, loaded)
