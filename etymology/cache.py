"""
SQLite-backed etymology cache.

Replaces the CSV-based master.csv with a proper database that supports
indexed lookups, atomic writes, and source tracking.
"""
import sqlite3
import os
import logging
from datetime import datetime

import pandas as pd

logger = logging.getLogger(__name__)

SCHEMA = """
CREATE TABLE IF NOT EXISTS etymologies (
    word TEXT PRIMARY KEY,
    root_word TEXT,
    root_language TEXT,
    second_language TEXT,
    ranked_languages TEXT,
    source TEXT DEFAULT 'unknown',
    lookup_date TEXT,
    raw_text TEXT
);
"""


class EtymologyCache:
    """SQLite-backed cache for etymology lookups."""

    def __init__(self, db_path="data/etymologies.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.executescript(SCHEMA)

    def close(self):
        self._conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def get(self, word):
        """Look up a single word. Returns dict or None."""
        row = self._conn.execute(
            "SELECT * FROM etymologies WHERE word = ?", (word.lower(),)
        ).fetchone()
        if row is None:
            return None
        return dict(row)

    def put(self, word, data):
        """Insert or update a word's etymology data.

        data should be a dict with keys like:
            root_word, root_language, second_language, ranked_languages,
            source, raw_text
        """
        now = datetime.utcnow().isoformat()
        self._conn.execute(
            """INSERT OR REPLACE INTO etymologies
               (word, root_word, root_language, second_language,
                ranked_languages, source, lookup_date, raw_text)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                word.lower(),
                data.get('root_word', ''),
                data.get('root_language', ''),
                data.get('second_language', ''),
                data.get('ranked_languages', ''),
                data.get('source', 'unknown'),
                now,
                data.get('raw_text', ''),
            )
        )
        self._conn.commit()

    def has(self, word):
        """Check if a word exists in the cache."""
        row = self._conn.execute(
            "SELECT 1 FROM etymologies WHERE word = ?", (word.lower(),)
        ).fetchone()
        return row is not None

    def bulk_get(self, words):
        """Look up multiple words at once. Returns dict of word -> data."""
        results = {}
        # SQLite has a variable limit; batch in groups of 500
        words_lower = [w.lower() for w in words]
        for i in range(0, len(words_lower), 500):
            batch = words_lower[i:i+500]
            placeholders = ','.join('?' * len(batch))
            rows = self._conn.execute(
                f"SELECT * FROM etymologies WHERE word IN ({placeholders})",
                batch
            ).fetchall()
            for row in rows:
                results[row['word']] = dict(row)
        return results

    def bulk_put(self, entries):
        """Insert or update multiple entries at once.

        entries: list of (word, data_dict) tuples
        """
        now = datetime.utcnow().isoformat()
        rows = []
        for word, data in entries:
            rows.append((
                word.lower(),
                data.get('root_word', ''),
                data.get('root_language', ''),
                data.get('second_language', ''),
                data.get('ranked_languages', ''),
                data.get('source', 'unknown'),
                now,
                data.get('raw_text', ''),
            ))
        self._conn.executemany(
            """INSERT OR REPLACE INTO etymologies
               (word, root_word, root_language, second_language,
                ranked_languages, source, lookup_date, raw_text)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            rows
        )
        self._conn.commit()
        logger.info("Bulk inserted %d entries into cache", len(rows))

    def count(self):
        """Return the number of entries in the cache."""
        row = self._conn.execute("SELECT COUNT(*) FROM etymologies").fetchone()
        return row[0]

    def import_csv(self, csv_path, source='csv_import'):
        """Import an existing CSV file (master.csv or *_etymologies.csv) into the cache.

        Expects CSV columns: word, root word, root language, second language, ranked languages
        """
        if not os.path.isfile(csv_path):
            logger.warning("CSV file not found: %s", csv_path)
            return 0

        df = pd.read_csv(csv_path)
        df.fillna('', inplace=True)

        imported = 0
        entries = []
        for _, row in df.iterrows():
            word = str(row.get('word', '')).lower().strip()
            if not word:
                continue
            root_lang = str(row.get('root language', ''))
            if not root_lang:
                continue

            data = {
                'root_word': str(row.get('root word', '')),
                'root_language': root_lang,
                'second_language': str(row.get('second language', '')),
                'ranked_languages': str(row.get('ranked languages', '')),
                'source': source,
            }
            entries.append((word, data))
            imported += 1

        if entries:
            self.bulk_put(entries)

        logger.info("Imported %d entries from %s", imported, csv_path)
        return imported


def migrate_csvs(csv_dir="csv", db_path="data/etymologies.db"):
    """One-time migration: import all existing CSV files into SQLite."""
    cache = EtymologyCache(db_path)

    # Import master first
    master_path = os.path.join(csv_dir, "master.csv")
    if os.path.isfile(master_path):
        cache.import_csv(master_path, source='master_csv')

    # Then import per-book etymologies (will update any missing entries)
    for fname in os.listdir(csv_dir):
        if fname.endswith('_etymologies.csv'):
            book = fname.replace('_etymologies.csv', '')
            cache.import_csv(os.path.join(csv_dir, fname), source=f'book_{book}')

    logger.info("Migration complete. Total entries: %d", cache.count())
    cache.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    migrate_csvs()
