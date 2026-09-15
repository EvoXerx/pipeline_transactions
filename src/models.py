from typing import TypedDict


class Transaction(TypedDict):
    datetime_transaction: str
    iban_origine: str
    pays_source: str
    banque_source: str
    iban_destinataire: str
    pays_destinataire: str
    montant: str
    devise: str


class FlaggedTransaction(Transaction):
    est_suspecte: bool


class LoadedFile(TypedDict):
    path: str
    content_hash: str
    transactions: list[Transaction]

