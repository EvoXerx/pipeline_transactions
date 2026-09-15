import csv
from pathlib import Path

from src.models import Transaction


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


TRANSACTIONS: list[Transaction] = [
    {
        "datetime_transaction": "2026-09-01T09:00:00",
        "iban_origine": "FR7611110000000000000000001",
        "pays_source": "France",
        "banque_source": "Banque Alpha",
        "iban_destinataire": "DE8922220000000000000000002",
        "pays_destinataire": "Allemagne",
        "montant": "1200.00",
        "devise": "EUR",
    },
    {
        "datetime_transaction": "2026-09-01T10:15:00",
        "iban_origine": "FR7633330000000000000000003",
        "pays_source": "France",
        "banque_source": "Banque Beta",
        "iban_destinataire": "ES9144440000000000000000004",
        "pays_destinataire": "Espagne",
        "montant": "6200.00",
        "devise": "EUR",
    },
    {
        "datetime_transaction": "2026-09-01T11:30:00",
        "iban_origine": "FR7611110000000000000000001",
        "pays_source": "France",
        "banque_source": "Banque Alpha",
        "iban_destinataire": "IT6055550000000000000000005",
        "pays_destinataire": "Italie",
        "montant": "850.50",
        "devise": "EUR",
    },
    {
        "datetime_transaction": "2026-09-01T13:00:00",
        "iban_origine": "BE7166660000000000000000006",
        "pays_source": "Belgique",
        "banque_source": "Banque Gamma",
        "iban_destinataire": "FR7677770000000000000000007",
        "pays_destinataire": "France",
        "montant": "9100.00",
        "devise": "EUR",
    },
    {
        "datetime_transaction": "2026-09-01T14:45:00",
        "iban_origine": "FR7633330000000000000000003",
        "pays_source": "France",
        "banque_source": "Banque Beta",
        "iban_destinataire": "FR7677770000000000000000007",
        "pays_destinataire": "France",
        "montant": "400.00",
        "devise": "EUR",
    },
    {
        "datetime_transaction": "2026-09-02T08:20:00",
        "iban_origine": "FR7611110000000000000000001",
        "pays_source": "France",
        "banque_source": "Banque Alpha",
        "iban_destinataire": "DE8922220000000000000000002",
        "pays_destinataire": "Allemagne",
        "montant": "3500.00",
        "devise": "EUR",
    },
    {
        "datetime_transaction": "2026-09-02T09:10:00",
        "iban_origine": "CH9388880000000000000000008",
        "pays_source": "Suisse",
        "banque_source": "Banque Delta",
        "iban_destinataire": "FR7699990000000000000000009",
        "pays_destinataire": "France",
        "montant": "5100.00",
        "devise": "EUR",
    },
    {
        "datetime_transaction": "2026-09-02T10:40:00",
        "iban_origine": "FR7633330000000000000000003",
        "pays_source": "France",
        "banque_source": "Banque Beta",
        "iban_destinataire": "ES9144440000000000000000004",
        "pays_destinataire": "Espagne",
        "montant": "2750.25",
        "devise": "EUR",
    },
    {
        "datetime_transaction": "2026-09-02T12:00:00",
        "iban_origine": "BE7166660000000000000000006",
        "pays_source": "Belgique",
        "banque_source": "Banque Gamma",
        "iban_destinataire": "FR7699990000000000000000009",
        "pays_destinataire": "France",
        "montant": "125.75",
        "devise": "EUR",
    },
    {
        "datetime_transaction": "2026-09-02T15:30:00",
        "iban_origine": "CH9388880000000000000000008",
        "pays_source": "Suisse",
        "banque_source": "Banque Delta",
        "iban_destinataire": "IT6055550000000000000000005",
        "pays_destinataire": "Italie",
        "montant": "7800.00",
        "devise": "EUR",
    },
]


def write_csv(path: Path, transactions: list[Transaction]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(transactions)


def generate_csv_files(output_dir: Path) -> list[Path]:
    paths = [output_dir / "transactions_01.csv", output_dir / "transactions_02.csv"]
    write_csv(paths[0], TRANSACTIONS[:5])
    write_csv(paths[1], TRANSACTIONS[5:])
    return paths


if __name__ == "__main__":
    generated = generate_csv_files(Path("data/input"))
    print(f"{len(generated)} fichiers CSV générés.")

