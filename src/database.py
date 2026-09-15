import sqlite3
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
    row_number INTEGER NOT NULL,
    datetime_transaction TEXT NOT NULL,
    iban_origine TEXT NOT NULL,
    pays_source TEXT NOT NULL,
    banque_source TEXT NOT NULL,
    iban_destinataire TEXT NOT NULL,
    pays_destinataire TEXT NOT NULL,
    montant REAL NOT NULL CHECK (montant >= 0),
    devise TEXT NOT NULL,
    est_suspecte INTEGER NOT NULL CHECK (est_suspecte IN (0, 1)),
    FOREIGN KEY (content_hash) REFERENCES processed_files(content_hash),
    UNIQUE (content_hash, row_number)
);

CREATE TABLE IF NOT EXISTS totals_sent_by_origin (
    content_hash TEXT NOT NULL,
    iban_origine TEXT NOT NULL,
    total REAL NOT NULL,
    PRIMARY KEY (content_hash, iban_origine),
    FOREIGN KEY (content_hash) REFERENCES processed_files(content_hash)
);

CREATE TABLE IF NOT EXISTS totals_sent_by_bank (
    content_hash TEXT NOT NULL,
    banque_source TEXT NOT NULL,
    total REAL NOT NULL,
    PRIMARY KEY (content_hash, banque_source),
    FOREIGN KEY (content_hash) REFERENCES processed_files(content_hash)
);

CREATE TABLE IF NOT EXISTS totals_received_by_iban (
    content_hash TEXT NOT NULL,
    iban_destinataire TEXT NOT NULL,
    total REAL NOT NULL,
    PRIMARY KEY (content_hash, iban_destinataire),
    FOREIGN KEY (content_hash) REFERENCES processed_files(content_hash)
);
"""


def setup_database(connection: sqlite3.Connection) -> None:
    connection.executescript(SCHEMA)


def _insert_loaded_file(connection: sqlite3.Connection, loaded: LoadedFile) -> bool:
    content_hash = loaded["content_hash"]
    try:
        connection.execute(
            "INSERT INTO processed_files(content_hash, original_name) VALUES (?, ?)",
            (content_hash, Path(loaded["path"]).name),
        )
    except sqlite3.IntegrityError:
        return False

    flagged = flag_transactions(loaded["transactions"])
    connection.executemany(
        """
        INSERT INTO transactions(
            content_hash, row_number, datetime_transaction, iban_origine,
            pays_source, banque_source, iban_destinataire, pays_destinataire,
            montant, devise, est_suspecte
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                content_hash,
                row_number,
                transaction["datetime_transaction"],
                transaction["iban_origine"],
                transaction["pays_source"],
                transaction["banque_source"],
                transaction["iban_destinataire"],
                transaction["pays_destinataire"],
                float(transaction["montant"]),
                transaction["devise"],
                int(transaction["est_suspecte"]),
            )
            for row_number, transaction in enumerate(flagged, start=1)
        ],
    )

    sent_by_origin = sum_sent_by_origin(loaded["transactions"])
    sent_by_bank = sum_sent_by_bank(loaded["transactions"])
    received_by_iban = sum_received_by_iban(loaded["transactions"])
    connection.executemany(
        "INSERT INTO totals_sent_by_origin VALUES (?, ?, ?)",
        [(content_hash, key, value) for key, value in sent_by_origin.items()],
    )
    connection.executemany(
        "INSERT INTO totals_sent_by_bank VALUES (?, ?, ?)",
        [(content_hash, key, value) for key, value in sent_by_bank.items()],
    )
    connection.executemany(
        "INSERT INTO totals_received_by_iban VALUES (?, ?, ?)",
        [(content_hash, key, value) for key, value in received_by_iban.items()],
    )
    return True


def insert_batch(db_path: Path, loaded_files: list[LoadedFile]) -> int:
    with sqlite3.connect(db_path) as connection:
        setup_database(connection)
        inserted = 0
        for loaded in loaded_files:
            inserted += int(_insert_loaded_file(connection, loaded))
        return inserted

