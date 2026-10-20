"""Read the supplied review-only subset; never contact or modify the operating DB.
Usage: python run_queries.py
Uses only Python's standard library. Query outputs are compared with saved CSVs.
"""
from pathlib import Path
import csv
import hashlib
import json
import sqlite3
import sys


def main() -> int:
    root = Path(__file__).resolve().parent
    database = root / 'inspection_review_subset.sqlite3'
    if len(sys.argv) != 1:
        raise ValueError('This tool accepts no DB path or other arguments.')
    if not database.is_file():
        raise FileNotFoundError('Extract the entire review_kit folder first.')
    metadata = json.loads((root / 'review_verification.json').read_text(encoding='utf-8'))
    before = hashlib.sha256(database.read_bytes()).hexdigest()
    if before != metadata['review_db_sha256']:
        raise ValueError('The review DB hash differs from the packaged reference.')
    definitions = json.loads((root / 'query_definitions.json').read_text(encoding='utf-8'))
    connection = sqlite3.connect(database.as_uri() + '?mode=ro&immutable=1', uri=True)
    connection.row_factory = sqlite3.Row
    try:
        connection.execute('PRAGMA query_only=ON')
        connection.execute("SELECT json_extract('{\"x\":1}', '$.x')")
        for item in definitions:
            actual = [dict(row) for row in connection.execute(item['sql'], item['parameters'])]
            with (root / 'query_results' / (item['name'] + '.csv')).open(encoding='utf-8-sig', newline='') as handle:
                expected = list(csv.DictReader(handle))
            display_values = [{key: '' if value is None else str(value) for key, value in row.items()} for row in actual]
            if display_values != expected:
                raise ValueError('Query output mismatch: ' + item['name'])
            print(f"{item['name']}: PASS ({len(actual)} rows)")
            print(json.dumps(actual, ensure_ascii=False, indent=2))
    finally:
        connection.close()
    if hashlib.sha256(database.read_bytes()).hexdigest() != before:
        raise ValueError('Unexpected review DB file change.')
    print('8 queries matched; review DB unchanged. No device connection performed.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, sqlite3.Error) as error:
        print('REVIEW FAILED: ' + str(error), file=sys.stderr)
        sys.exit(1)
