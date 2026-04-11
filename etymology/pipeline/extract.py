"""
Stage 1: Gutenberg HTML -> word list with frequency counts.

Parses a Project Gutenberg HTML file, extracts all paragraph text,
tokenizes with TextBlob, and returns a sorted word-frequency list.
"""
import logging
import os

from bs4 import BeautifulSoup
from textblob import TextBlob

logger = logging.getLogger(__name__)


def extract_words(html_path):
    """Extract unique words and their counts from a Gutenberg HTML file.

    Args:
        html_path: Path to the Gutenberg HTML file.

    Returns:
        List of (word, count) tuples sorted by count descending, then word ascending.
    """
    if not os.path.isfile(html_path):
        raise FileNotFoundError(f"Gutenberg file not found: {html_path}")

    logger.info("Opening HTML: %s", html_path)
    with open(html_path, 'r', encoding='utf-8') as f:
        html_doc = f.read()
    soup = BeautifulSoup(html_doc, 'html.parser')

    # Extract paragraph text, skipping table-of-contents entries
    logger.info("Extracting paragraph text...")
    texttags_all = soup.findAll('p', text=True)
    texttags = []
    for tag in texttags_all:
        if 'class' in tag.attrs:
            if tag.attrs['class'] == 'toc':
                continue
        texttags.append(tag)
    logger.info("Found %d paragraphs", len(texttags))

    all_text = []
    for tag in texttags:
        if tag.string:
            all_text.append(str(tag.string))

    full_text = " ".join(all_text)

    logger.info("Tokenizing with TextBlob...")
    blob = TextBlob(full_text)
    wc = blob.word_counts

    # Build sorted list
    word_counts = [(word.lower(), count) for word, count in wc.items()]
    word_counts.sort(key=lambda x: (-x[1], x[0]))

    logger.info("Extracted %d unique words", len(word_counts))
    return word_counts


def save_word_list(word_counts, csv_path):
    """Save word counts to CSV."""
    import pandas as pd
    df = pd.DataFrame(word_counts, columns=['word', 'word count'])
    df.index = range(1, len(df) + 1)
    df.to_csv(csv_path, index=False, na_rep="")
    logger.info("Saved word list to %s", csv_path)


def load_word_list(csv_path):
    """Load a previously saved word list."""
    import pandas as pd
    df = pd.read_csv(csv_path)
    return list(zip(df['word'].values, df['word count'].values))
