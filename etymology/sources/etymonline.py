"""
Etymonline.com source — wraps the existing scraping logic using requests + BeautifulSoup.

Replaces the old mechanize-based browser automation with direct HTTP requests,
adds HTTPS, User-Agent header, and retry with exponential backoff.
"""
import logging
import re
import time
from typing import Optional, Dict, List

import requests
from bs4 import BeautifulSoup
from textblob import Word

from etymology.sources.base import EtymologySource
from etymology.languages import languages

logger = logging.getLogger(__name__)

SEARCH_URL = "https://www.etymonline.com/search"
USER_AGENT = "WordsWordsWords/1.0 (etymology research project)"
MAX_RETRIES = 3
RETRY_BACKOFF = 2.0


class EtymonlineSource(EtymologySource):
    """Etymology source that queries etymonline.com via HTTP."""

    @property
    def name(self) -> str:
        return "etymonline"

    def available(self) -> bool:
        try:
            resp = requests.head(SEARCH_URL, timeout=5,
                                 headers={"User-Agent": USER_AGENT})
            return resp.status_code < 500
        except Exception:
            return False

    def lookup(self, word: str) -> Optional[Dict]:
        """Look up a word, trying the original form first, then root variants."""
        # Try exact match
        result = self._try_lookup(word, word)
        if result:
            return result

        # Try root word variants
        roots = self._get_root_word(word)
        for root in roots:
            result = self._try_lookup(root, root)
            if result:
                result['root_word'] = root
                return result

        return None

    def _try_lookup(self, search_word: str, original_word: str) -> Optional[Dict]:
        """Attempt a single lookup on etymonline.com."""
        soup = self._fetch(search_word)
        if soup is None:
            return None

        dts = soup.find_all('dt')
        dds = soup.find_all('dd')

        for dt, dd in zip(dts, dds):
            term_full = dt.get_text()

            if search_word.lower() != 'the':
                term = term_full.split(' ')[0].strip()
            else:
                term = term_full.strip()

            if search_word.lower() == term.lower():
                etym_text = dd.get_text()
                result = self._parse_languages(etym_text)
                result['root_word'] = original_word
                result['raw_text'] = etym_text
                return result

        return None

    def _fetch(self, word: str) -> Optional[BeautifulSoup]:
        """Fetch search results from etymonline.com with retry."""
        for attempt in range(MAX_RETRIES):
            try:
                resp = requests.get(
                    SEARCH_URL,
                    params={"q": word},
                    headers={"User-Agent": USER_AGENT},
                    timeout=15,
                )
                if resp.status_code == 200:
                    return BeautifulSoup(resp.text, 'html.parser')
                elif resp.status_code == 429:
                    wait = RETRY_BACKOFF * (2 ** attempt)
                    logger.warning("Rate limited by etymonline, waiting %.1fs", wait)
                    time.sleep(wait)
                else:
                    logger.warning("Etymonline returned %d for '%s'", resp.status_code, word)
                    return None
            except requests.RequestException as e:
                if attempt < MAX_RETRIES - 1:
                    wait = RETRY_BACKOFF * (2 ** attempt)
                    logger.warning("Request failed for '%s', retrying in %.1fs: %s", word, wait, e)
                    time.sleep(wait)
                else:
                    logger.error("All retries exhausted for '%s': %s", word, e)
                    return None
        return None

    def _parse_languages(self, etymology_text: str) -> Dict:
        """Parse an etymology text to extract language origins.

        Uses regex to find language references and ranks them by position.
        Preserves the original logic from EtymologyCSV.
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

    def _get_root_word(self, the_word: str) -> List[str]:
        """Generate root word candidates by stripping common suffixes.

        Ported from the original EtymologyCSV.get_root_word().
        """
        synset = []

        try:
            full_synset = Word(the_word).synsets
            full_synset_strings = [syn.name().split('.')[0] for syn in full_synset]
        except Exception:
            full_synset_strings = []

        for sss in full_synset_strings:
            if sss[:3] == the_word[:3]:
                synset.append(sss)

        if len(the_word) > 4:
            if the_word[-2:] == 'ed':
                if the_word[-4] == the_word[-3]:
                    synset.insert(0, the_word[:-3])
                elif the_word[-3:] == 'ied':
                    synset.insert(0, the_word[:-3] + "y")
                else:
                    synset.insert(0, the_word[:-2])
                    synset.append(the_word[:-1])

            if the_word[-2:] == 'en':
                synset.insert(0, the_word[:-2])
                synset.append(the_word[:-1])

            if the_word[-2:] == 'er':
                synset.insert(0, the_word[:-2])
                synset.append(the_word[:-1])

            if the_word[-3:] == 'est':
                synset.insert(0, the_word[:-3])
                synset.append(the_word[:-2])

            if the_word[-3:] == 'ing':
                synset.insert(0, the_word[:-3])
                synset.append(the_word[:-4])
                synset.append(the_word[:-3] + "e")

            if the_word[-2:] == 'ly':
                synset.insert(0, the_word[:-2])

        if the_word[-1:] == 's':
            if len(the_word) > 6:
                if the_word[-6:] == 'liness':
                    synset.insert(0, the_word[:-6])
                elif the_word[-5:] == 'iness':
                    synset.insert(0, the_word[:-5] + "y")

            if the_word[-2:] == 'es':
                if the_word[-3:] == 'ies':
                    synset.insert(0, the_word[:-3] + "y")
                else:
                    synset.insert(0, the_word[:-2])
                    synset.append(the_word[:-1])
            else:
                synset.insert(0, the_word[:-1])

        if len(the_word) > 5:
            if the_word[-5:] == 'ation':
                synset.insert(0, the_word[:-5] + "ate")

        return synset
