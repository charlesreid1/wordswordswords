"""
Wiktionary API source — free, no auth, CC-licensed.

Fetches the HTML page for a word from the Wiktionary REST API,
extracts the Etymology section, and parses language references
using the same regex logic as the etymonline source.
"""
import logging
import re
import time
from typing import Optional, Dict

import requests
from bs4 import BeautifulSoup

from etymology.sources.base import EtymologySource
from etymology.languages import languages

logger = logging.getLogger(__name__)

API_BASE = "https://en.wiktionary.org/api/rest_v1/page/html"
USER_AGENT = "WordsWordsWords/1.0 (etymology research project; https://github.com/charlesreid1/wordswordswords)"
MAX_RETRIES = 2
RETRY_BACKOFF = 1.0


class WiktionarySource(EtymologySource):
    """Etymology source using the Wiktionary REST API."""

    @property
    def name(self) -> str:
        return "wiktionary"

    def available(self) -> bool:
        try:
            resp = requests.head(
                f"{API_BASE}/test",
                headers={"User-Agent": USER_AGENT},
                timeout=5,
            )
            return resp.status_code < 500
        except Exception:
            return False

    def lookup(self, word: str) -> Optional[Dict]:
        """Look up a word's etymology via Wiktionary."""
        html = self._fetch(word)
        if html is None:
            return None

        etym_text = self._extract_etymology(html)
        if not etym_text:
            return None

        result = self._parse_languages(etym_text)
        if not result.get('root_language'):
            return None

        result['root_word'] = word
        result['raw_text'] = etym_text
        return result

    def _fetch(self, word: str) -> Optional[str]:
        """Fetch the Wiktionary HTML page for a word."""
        url = f"{API_BASE}/{word}"

        for attempt in range(MAX_RETRIES):
            try:
                resp = requests.get(
                    url,
                    headers={"User-Agent": USER_AGENT},
                    timeout=15,
                )
                if resp.status_code == 200:
                    return resp.text
                elif resp.status_code == 404:
                    return None
                elif resp.status_code == 429:
                    wait = RETRY_BACKOFF * (2 ** attempt)
                    logger.warning("Rate limited by Wiktionary, waiting %.1fs", wait)
                    time.sleep(wait)
                else:
                    logger.warning("Wiktionary returned %d for '%s'", resp.status_code, word)
                    return None
            except requests.RequestException as e:
                if attempt < MAX_RETRIES - 1:
                    wait = RETRY_BACKOFF * (2 ** attempt)
                    logger.warning("Wiktionary request failed for '%s', retrying: %s", word, e)
                    time.sleep(wait)
                else:
                    logger.error("All retries exhausted for '%s': %s", word, e)
                    return None
        return None

    def _extract_etymology(self, html: str) -> Optional[str]:
        """Extract the Etymology section text from a Wiktionary HTML page.

        Wiktionary pages have sections marked with <h3> or <h4> headings
        containing "Etymology". We grab all text between that heading
        and the next heading of equal or higher level.
        """
        soup = BeautifulSoup(html, 'html.parser')

        # Find the Etymology heading
        etym_heading = None
        for heading in soup.find_all(['h2', 'h3', 'h4']):
            heading_text = heading.get_text(strip=True)
            if heading_text.startswith('Etymology'):
                etym_heading = heading
                break

        if etym_heading is None:
            return None

        # Collect all text between this heading and the next heading
        heading_level = etym_heading.name  # e.g., 'h3'
        text_parts = []

        for sibling in etym_heading.find_next_siblings():
            if sibling.name in ['h2', 'h3', 'h4']:
                # Stop at next heading of same or higher level
                if sibling.name <= heading_level:
                    break
            text = sibling.get_text(separator=' ', strip=True)
            if text:
                text_parts.append(text)

        return ' '.join(text_parts) if text_parts else None

    def _parse_languages(self, etymology_text: str) -> Dict:
        """Parse language references from etymology text.

        Same regex logic as the etymonline source for consistency.
        """
        etymology_grid = []

        for lang in languages:
            m = re.search(lang + r'\b', etymology_text)
            n = re.search('Old ' + lang + r'\b', etymology_text)

            if m and not n:
                etymology_grid.append(m.start())
            else:
                etymology_grid.append(-1)

        etymology_grid_gt0 = [eg for eg in etymology_grid if eg >= 0]

        if not etymology_grid_gt0:
            return {
                'root_language': '',
                'second_language': '',
                'ranked_languages': '',
            }

        sorted_grid = sorted(etymology_grid_gt0)
        ranked_langs = [''] * len(etymology_grid_gt0)
        ranking = []
        for et in etymology_grid:
            if et >= 0:
                ranking.append(sorted_grid.index(et))
            else:
                ranking.append(-1)

        for i, r in enumerate(ranking):
            if r > -1:
                ranked_langs[r] = languages[i]

        return {
            'root_language': ranked_langs[0] if ranked_langs else '',
            'second_language': ranked_langs[1] if len(ranked_langs) > 1 else '',
            'ranked_languages': ";".join(ranked_langs),
        }
