"""
WordNet/NLTK lemmatizer source.

This is not an etymology source per se — it improves root-word detection
by using NLTK's WordNetLemmatizer instead of hand-rolled suffix stripping.
It wraps another source, lemmatizing words before passing them through.
"""
import logging
from typing import Optional, Dict

from etymology.sources.base import EtymologySource

logger = logging.getLogger(__name__)

_lemmatizer = None


def _get_lemmatizer():
    """Lazy-load the NLTK WordNet lemmatizer and data."""
    global _lemmatizer
    if _lemmatizer is None:
        try:
            import nltk
            nltk.download('wordnet', quiet=True)
            nltk.download('omw-1.4', quiet=True)
            from nltk.stem import WordNetLemmatizer
            _lemmatizer = WordNetLemmatizer()
        except ImportError:
            logger.warning("NLTK not installed. WordNet lemmatizer unavailable.")
            return None
    return _lemmatizer


def lemmatize(word: str) -> list:
    """Return lemmatized forms of a word.

    Tries noun, verb, adjective, and adverb POS tags.
    Returns a deduplicated list of unique lemmas (excluding the original word).
    """
    lem = _get_lemmatizer()
    if lem is None:
        return []

    lemmas = set()
    for pos in ('n', 'v', 'a', 'r'):  # noun, verb, adj, adverb
        result = lem.lemmatize(word, pos=pos)
        if result != word:
            lemmas.add(result)

    return list(lemmas)


class WordNetLemmatizerSource(EtymologySource):
    """Wraps another etymology source with WordNet lemmatization.

    If the inner source can't find the word directly, this source
    tries lemmatized forms before giving up.
    """

    def __init__(self, inner_source: EtymologySource):
        self._inner = inner_source

    @property
    def name(self) -> str:
        return f"wordnet+{self._inner.name}"

    def available(self) -> bool:
        return _get_lemmatizer() is not None and self._inner.available()

    def lookup(self, word: str) -> Optional[Dict]:
        # First try the word directly with the inner source
        result = self._inner.lookup(word)
        if result and result.get('root_language'):
            return result

        # Try lemmatized forms
        lemmas = lemmatize(word)
        for lemma in lemmas:
            logger.debug("Trying lemma '%s' for '%s'", lemma, word)
            result = self._inner.lookup(lemma)
            if result and result.get('root_language'):
                result['root_word'] = lemma
                return result

        return None
