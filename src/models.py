from decimal import Decimal
from typing import TypedDict


CSV_COLUMNS = [
    "datetime_transaction",
    "iban_origine",
    "pays_source",
    "banque_source",
    "iban_destinataire",
    "pays_destinataire",
    "montant",
    "devise",
]


class Transaction(TypedDict):
    datetime_transaction: str
    iban_origine: str
    pays_source: str
    banque_source: str
    iban_destinataire: str
    pays_destinataire: str
    montant: Decimal
    devise: str


class FlaggedTransaction(Transaction):
    est_suspecte: bool


class LoadedFile(TypedDict):
    path: str
    content_hash: str
    transactions: list[Transaction]
