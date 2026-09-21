from collections.abc import Callable
from decimal import Decimal

from src.models import FlaggedTransaction, Transaction


def _sum_by(
    transactions: list[Transaction], key: Callable[[Transaction], str]
) -> dict[str, Decimal]:
    totals: dict[str, Decimal] = {}
    for transaction in transactions:
        name = key(transaction)
        totals[name] = totals.get(name, Decimal(0)) + transaction["montant"]
    return totals


def sum_sent_by_origin(transactions: list[Transaction]) -> dict[str, Decimal]:
    return _sum_by(transactions, lambda t: t["iban_origine"])


def sum_sent_by_bank(transactions: list[Transaction]) -> dict[str, Decimal]:
    return _sum_by(transactions, lambda t: t["banque_source"])


def sum_received_by_iban(transactions: list[Transaction]) -> dict[str, Decimal]:
    return _sum_by(transactions, lambda t: t["iban_destinataire"])


def flag_transactions(
    transactions: list[Transaction], threshold: Decimal = Decimal("5000")
) -> list[FlaggedTransaction]:
    return [
        FlaggedTransaction(**transaction, est_suspecte=transaction["montant"] > threshold)
        for transaction in transactions
    ]
