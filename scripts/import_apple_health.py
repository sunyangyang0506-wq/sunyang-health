"""Import Apple Health neutral JSON records into the local health database.

Usage:
  python scripts/import_apple_health.py data/raw/apple_health.json

Input: JSON array of records with type, value, unit, start_date and optional source.
"""
import json
import sys
from pathlib import Path

from app.services.health_pipeline import ingest_apple_health


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python scripts/import_apple_health.py <records.json>')
    path = Path(sys.argv[1])
    records = json.loads(path.read_text(encoding='utf-8'))
    result = ingest_apple_health(records)
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == '__main__':
    main()
