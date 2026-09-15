from copy import deepcopy

from src.models import Transaction
from src.processing import (
    flag_transactions,
    sum_received_by_iban,
    sum_sent_by_bank,
    sum_sent_by_origin,
)


SAMPLE: list[Transaction] = [
    {
        "datetime_transaction": "2026-01-01T10:00:00",
        "iban_origine": "FR-A",
        "pays_source": "France",
        "banque_source": "Banque A",
        "iban_destinataire": "FR-X",
        "pays_destinataire": "France",
        "montant": "1000.00",
        "devise": "EUR",
    },
    {
        "datetime_transaction": "2026-01-01T11:00:00",
        "iban_origine": "FR-A",
        "pays_source": "France",
        "banque_source": "Banque A",
        "iban_destinataire": "FR-Y",
        "pays_destinataire": "France",
        "montant": "6000.00",
        "devise": "EUR",
    },
    {
        "datetime_transaction": "2026-01-01T12:00:00",
        "iban_origine": "FR-B",
        "pays_source": "France",
        "banque_source": "Banque B",
        "iban_destinataire": "FR-X",
        "pays_destinataire": "France",
        "montant": "5000.00",
        "devise": "EUR",
    },
]


def test_sum_sent_by_origin() -> None:
    assert sum_sent_by_origin(SAMPLE) == {"FR-A": 7000.0, "FR-B": 5000.0}


def test_sum_sent_by_bank() -> None:
    assert sum_sent_by_bank(SAMPLE) == {"Banque A": 7000.0, "Banque B": 5000.0}


def test_sum_received_by_iban() -> None:
    assert sum_received_by_iban(SAMPLE) == {"FR-X": 6000.0, "FR-Y": 6000.0}


def test_flag_transactions_and_purity() -> None:
    before = deepcopy(SAMPLE)
    result = flag_transactions(SAMPLE)
    assert [item["est_suspecte"] for item in result] == [False, True, False]
    assert SAMPLE == before

