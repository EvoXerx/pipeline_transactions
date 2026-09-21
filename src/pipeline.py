import sqlite3
import sys
from pathlib import Path

from src.database import insert_with_retry
from src.generator import generate_csv_files
from src.loader import load_file


def run(input_dir: Path, db_path: Path) -> int:
    generate_csv_files(input_dir)
    failed = 0
    for path in sorted(input_dir.glob("*.csv")):
        try:
            inserted = insert_with_retry(db_path, load_file(path))
        except (ValueError, sqlite3.Error) as error:
            print(f"ÉCHEC {path.name} : {error}")
            failed += 1
        else:
            print(f"{'OK' if inserted else 'IGNORÉ (déjà traité)'} {path.name}")
    return 1 if failed else 0


if __name__ == "__main__":
    input_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/input")
    db_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("data/pipeline.db")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    sys.exit(run(input_dir, db_path))
