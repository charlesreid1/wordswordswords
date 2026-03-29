"""
Stage 3: etymology data + Gutenberg HTML -> tagged HTML.

Takes etymology lookup results and the original Gutenberg HTML,
wraps each word in a language-colored <span> tag, and outputs
tagged HTML files (per-chapter or whole-book).
"""
import logging
import os
import re
import string

from bs4 import BeautifulSoup

from etymology.languages import languages_key

logger = logging.getLogger(__name__)


def build_etymology_lookup(etymology_data):
    """Build a dict for O(1) word -> CSS class lookups.

    Args:
        etymology_data: Dict mapping word -> data dict with 'root_language' key,
                        OR a pandas DataFrame with 'word' and 'root language' columns.

    Returns:
        Dict mapping lowercase word -> CSS class name.
    """
    lookup = {}

    if hasattr(etymology_data, 'iterrows'):
        # pandas DataFrame
        for _, row in etymology_data.iterrows():
            word = str(row.get('word', '')).lower()
            lang = str(row.get('root language', '') or row.get('root_language', ''))
            if word and lang and lang in languages_key:
                lookup[word] = languages_key[lang]
    else:
        # dict from lookup stage
        for word, data in etymology_data.items():
            if isinstance(data, dict):
                lang = data.get('root_language', '') or data.get('root language', '')
                if lang and lang in languages_key:
                    lookup[word.lower()] = languages_key[lang]

    return lookup


def tag_tokens(tokens, etymology_lookup):
    """Tag a list of tokens with etymology spans.

    Args:
        tokens: List of string tokens (words, possibly with punctuation).
        etymology_lookup: Dict from build_etymology_lookup().

    Returns:
        List of tokens with matches wrapped in <span class="lang"> tags.
    """
    for i, token in enumerate(tokens):
        stripped = token.lower().strip(string.punctuation)
        if stripped in etymology_lookup:
            lang = etymology_lookup[stripped]
            tokens[i] = f'<span class="{lang}">{token}</span>'
    return tokens


def generate_chapter_html(gutenberg_path, etymology_data, output_dir, book_name):
    """Generate per-chapter tagged HTML files.

    Args:
        gutenberg_path: Path to Gutenberg HTML source file.
        etymology_data: Either a dict (from lookup stage) or a DataFrame.
        output_dir: Directory to write chapter HTML files.
        book_name: Base name for output files (e.g. 'dubliners').
    """
    etymology_lookup = build_etymology_lookup(etymology_data)
    logger.info("Built etymology lookup with %d entries", len(etymology_lookup))

    with open(gutenberg_path, 'r', encoding='utf-8') as f:
        html_doc = f.read()
    soup = BeautifulSoup(html_doc, 'html.parser')

    os.makedirs(output_dir, exist_ok=True)

    # Extract title and author
    titletag = soup.findAll('h1', text=True)[0]
    title = titletag.string

    authortag = soup.findAll('h2', text=True)[0]
    author = re.sub('By ', '', authortag.string)

    h2tags = soup.findAll('h2', text=True)[1:]  # skip author heading

    ich = 1
    for h2tag in h2tags:
        logger.info("Tagging chapter %d", ich)

        new_body = [str(h2tag)]
        chapter_file = f"{book_name}{ich}.html"

        nexttag = h2tag.findNextSibling(['p', 'h2'])
        if nexttag is None:
            break

        ip = 0
        while True:
            if nexttag.name == 'h2':
                break
            if nexttag is None:
                break

            ip += 1

            try:
                tokens = nexttag.string.split()
            except AttributeError:
                tokens = []

            if tokens:
                tokens = tag_tokens(tokens, etymology_lookup)
                new_body.append(' '.join(tokens))

            nexttag = nexttag.findNextSibling(['p', 'h2'])
            if nexttag is None:
                break

        logger.info("Chapter %d: %d paragraphs", ich, ip)

        chapter_soup = BeautifulSoup(' '.join(new_body), 'html.parser')
        chapter_path = os.path.join(output_dir, chapter_file)
        with open(chapter_path, 'w', encoding='utf-8') as f:
            f.write(chapter_soup.prettify())

        ich += 1

    logger.info("Generated %d chapter files in %s", ich - 1, output_dir)


def generate_full_html(gutenberg_path, etymology_data, output_path, book_name):
    """Generate a single tagged HTML file for the full book.

    Args:
        gutenberg_path: Path to Gutenberg HTML source file.
        etymology_data: Either a dict (from lookup stage) or a DataFrame.
        output_path: Path for the output HTML file.
        book_name: Used for meta tags.
    """
    etymology_lookup = build_etymology_lookup(etymology_data)
    logger.info("Built etymology lookup with %d entries", len(etymology_lookup))

    with open(gutenberg_path, 'r', encoding='utf-8') as f:
        html_doc = f.read()
    soup = BeautifulSoup(html_doc, 'html.parser')

    titletag = soup.findAll('h1', text=True)[0]
    title = titletag.string

    authortag = soup.findAll('h2', text=True)[0]
    author = re.sub('By ', '', authortag.string)

    new_body = [
        f"<html><head><title>{title}</title>",
        f'<meta name="author" content="{author}" />',
        f'<meta name="save_as" content="{book_name}.html" />',
        "</head><body>",
    ]

    booktags = soup.findAll(['p', 'h2'], text=True)
    logger.info("Processing %d tags", len(booktags))

    for booktag in booktags:
        if booktag.name == 'h2':
            new_body.append(str(booktag))

        elif booktag.name == 'p' and booktag.string is not None:
            tokens = booktag.string.split()
            tokens = tag_tokens(tokens, etymology_lookup)
            new_body.append("<p>" + ' '.join(tokens) + "</p>")

    new_body.append("</body></html>")

    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    final_soup = BeautifulSoup(' '.join(new_body), 'html.parser')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_soup.prettify())

    logger.info("Written full HTML to %s", output_path)
