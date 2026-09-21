from copy import deepcopy
from decimal import Decimal

from src.models import Transaction
from src.processing import (
    flag_transactions,
    sum_received_by_iban,
    sum_sent_by_bank,
    sum_sent_by_origin,
)


def make(origin: str, bank: str, dest: str, montant: str) -> Transaction:
    return {
        "datetime_transaction": "2026-01-01T10:00:00",
        "iban_origine": origin,
        "pays_source": "France",
        "banque_source": bank,
        "iban_destinataire": dest,
        "pays_destinataire": "France",
        "montant": Decimal(montant),
        "devise": "EUR",
    }


SAMPLE = [
    make("FR-A", "Banque A", "FR-X", "1234.56"),
    make("FR-A", "Banque A", "FR-Y", "7250.75"),
    make("FR-B", "Banque B", "FR-X", "5000.00"),
]


def test_sum_sent_by_origin() -> None:
    assert sum_sent_by_origin(SAMPLE) == {"FR-A": Decimal("8485.31"), "FR-B": Decimal("5000")}


def test_sum_sent_by_bank() -> None:
    assert sum_sent_by_bank(SAMPLE) == {"Banque A": Decimal("8485.31"), "Banque B": Decimal("5000")}


def test_sum_received_by_iban() -> None:
    assert sum_received_by_iban(SAMPLE) == {"FR-X": Decimal("6234.56"), "FR-Y": Decimal("7250.75")}


def test_flag_transactions_and_purity() -> None:
    before = deepcopy(SAMPLE)
    result = flag_transactions(SAMPLE)
    assert [item["est_suspecte"] for item in result] == [False, True, False]
    assert SAMPLE == before
