from src.models import FlaggedTransaction, Transaction


def sum_sent_by_origin(transactions: list[Transaction]) -> dict[str, float]:
    totals: dict[str, float] = {}
    for transaction in transactions:
        iban = transaction["iban_origine"]
        totals[iban] = totals.get(iban, 0.0) + float(transaction["montant"])
    return totals


def sum_sent_by_bank(transactions: list[Transaction]) -> dict[str, float]:
    totals: dict[str, float] = {}
    for transaction in transactions:
        banque = transaction["banque_source"]
        totals[banque] = totals.get(banque, 0.0) + float(transaction["montant"])
    return totals


def sum_received_by_iban(transactions: list[Transaction]) -> dict[str, float]:
    totals: dict[str, float] = {}
    for transaction in transactions:
        iban = transaction["iban_destinataire"]
        totals[iban] = totals.get(iban, 0.0) + float(transaction["montant"])
    return totals


def flag_transactions(
    transactions: list[Transaction], threshold: float = 5000.0
) -> list[FlaggedTransaction]:
    return [
        FlaggedTransaction(
            **transaction,
            est_suspecte=float(transaction["montant"]) > threshold,
        )
        for transaction in transactions
    ]

