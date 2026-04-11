#!/usr/bin/env python3
"""
Unified CLI entry point for the Words Words Words etymology pipeline.

Supports two modes:
  --mode legacy   Uses the original EtymologyCSV/EtymologyChapterHTML classes
  --mode pipeline Uses the new modular pipeline (extract → lookup → generate)

Usage:
    # Legacy mode (default)
    python -m etymology.run --book frankenstein --step csv
    python -m etymology.run --book frankenstein --step html
    python -m etymology.run --book frankenstein --step all

    # New pipeline mode
    python -m etymology.run --mode pipeline --book frankenstein --step all

    # Migrate existing CSVs to SQLite cache
    python -m etymology.run --migrate
"""
import argparse
import logging
import os
import sys

import yaml


def get_known_books():
    """Load known books from the root books.yaml."""
    yaml_path = os.path.join(os.path.dirname(__file__), '..', 'books.yaml')
    if os.path.isfile(yaml_path):
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
            if data:
                return list(data.keys())
    return [
        'copperfield',
        'crimeandpunishment',
        'dubliners',
        'frankenstein',
        'leviathan',
        'roughingit',
        'treatisegovt',
        'ulysses',
        'variableman',
    ]

KNOWN_BOOKS = get_known_books()


def load_config(config_path="config.yaml"):
    """Load configuration from YAML file."""
    if os.path.isfile(config_path):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return {
        'sources': ['wiktionary', 'etymonline'],
        'use_wordnet_lemmatizer': False,
        'rate_limits': {'etymonline': 2.0, 'wiktionary': 0.5},
        'max_workers': 3,
        'cache_db': 'data/etymologies.db',
        'llm': {'model': 'claude-sonnet-4-6'},
    }


def build_source_chain(config):
    """Build a SourceChain from config."""
    from etymology.sources import SourceChain
    from etymology.sources.etymonline import EtymonlineSource
    from etymology.sources.wiktionary import WiktionarySource
    from etymology.sources.llm import LLMSource

    source_map = {
        'etymonline': EtymonlineSource,
        'wiktionary': WiktionarySource,
        'llm': lambda: LLMSource(model=config.get('llm', {}).get('model', 'claude-sonnet-4-6')),
    }

    sources = []
    for name in config.get('sources', ['wiktionary', 'etymonline']):
        factory = source_map.get(name)
        if factory:
            source = factory() if callable(factory) else factory
            sources.append(source)
        else:
            logging.warning("Unknown source: %s", name)

    # Optionally wrap the first source with WordNet lemmatization
    if config.get('use_wordnet_lemmatizer') and sources:
        from etymology.sources.wordnet import WordNetLemmatizerSource
        sources[0] = WordNetLemmatizerSource(sources[0])

    return SourceChain(sources)


def run_legacy(book, step):
    """Run using the original monolithic classes."""
    from etymology.etymology_csv import EtymologyCSV
    from etymology.etymology_chapter_html import EtymologyChapterHTML

    if step in ('csv', 'all'):
        c = EtymologyCSV(book)
        c.export_csv()

    if step in ('html', 'all'):
        h = EtymologyChapterHTML(book)
        h.export_html_file()


def run_pipeline(book, step, config):
    """Run using the new modular pipeline."""
    from etymology.pipeline.extract import extract_words, save_word_list, load_word_list
    from etymology.pipeline.lookup import lookup_words
    from etymology.pipeline.generate import generate_chapter_html
    from etymology.cache import EtymologyCache

    gutenberg_path = f"gutenberg/{book}.html"
    words_csv = f"csv/{book}_words.csv"
    cache_db = config.get('cache_db', 'data/etymologies.db')
    progress_path = f"data/{book}_progress.json"

    cache = EtymologyCache(cache_db)

    if step in ('extract', 'csv', 'all'):
        # Stage 1: Extract words
        if os.path.isfile(words_csv):
            logging.info("Loading existing word list from %s", words_csv)
            word_counts = load_word_list(words_csv)
        else:
            word_counts = extract_words(gutenberg_path)
            save_word_list(word_counts, words_csv)

    if step in ('lookup', 'csv', 'all'):
        # Stage 2: Look up etymologies
        if 'word_counts' not in locals():
            word_counts = load_word_list(words_csv)

        source_chain = build_source_chain(config)
        rate_limit = max(
            config.get('rate_limits', {}).values() or [2.0]
        )

        etymology_data = lookup_words(
            word_counts,
            cache=cache,
            source_chain=source_chain,
            max_workers=config.get('max_workers', 3),
            rate_limit=rate_limit,
            progress_path=progress_path,
        )

    if step in ('html', 'generate', 'all'):
        # Stage 3: Generate tagged HTML
        # If we don't have etymology_data from lookup, load from cache
        if 'etymology_data' not in locals():
            if os.path.isfile(words_csv):
                word_counts = load_word_list(words_csv)
                word_list = [w for w, _ in word_counts]
                etymology_data = cache.bulk_get(word_list)
            else:
                # Fall back to CSV
                import pandas as pd
                etym_csv = f"csv/{book}_etymologies.csv"
                etymology_data = pd.read_csv(etym_csv).fillna("")

        # Standard output dir for Pelican templates
        pelican_output = "pelican/cmr-pelican-theme/templates/_includes"
        
        generate_chapter_html(
            gutenberg_path=gutenberg_path,
            etymology_data=etymology_data,
            output_dir=pelican_output,
            book_name=book,
        )

    cache.close()


def run_migrate():
    """Migrate existing CSV files to SQLite cache."""
    from etymology.cache import migrate_csvs
    migrate_csvs()


def main():
    parser = argparse.ArgumentParser(
        description='Words Words Words — Etymological text analysis pipeline'
    )
    parser.add_argument(
        '--book',
        help='Book name (e.g. frankenstein, dubliners, ulysses)'
    )
    parser.add_argument(
        '--step', choices=['extract', 'lookup', 'csv', 'html', 'generate', 'all'],
        help='Pipeline step to run'
    )
    parser.add_argument(
        '--mode', default='pipeline', choices=['legacy', 'pipeline'],
        help='Execution mode: legacy (original classes) or pipeline (new modular system)'
    )
    parser.add_argument(
        '--config', default='config.yaml',
        help='Path to config.yaml (default: config.yaml)'
    )
    parser.add_argument(
        '--migrate', action='store_true',
        help='Migrate existing CSV files to SQLite cache'
    )
    parser.add_argument(
        '--log-level', default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level (default: INFO)'
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s %(name)s %(levelname)s: %(message)s',
        datefmt='%H:%M:%S'
    )

    if args.migrate:
        run_migrate()
        return

    if not args.book or not args.step:
        parser.error("--book and --step are required unless using --migrate")

    books_to_process = [args.book]
    if args.book == 'all':
        books_to_process = KNOWN_BOOKS

    for book in books_to_process:
        if book not in KNOWN_BOOKS and args.book != 'all':
            logging.warning("Book '%s' is not in the known books list. Proceeding anyway.", book)

        logging.info("Processing book: %s", book)
        if args.mode == 'legacy':
            run_legacy(book, args.step)
        else:
            config = load_config(args.config)
            run_pipeline(book, args.step, config)


if __name__ == '__main__':
    main()
