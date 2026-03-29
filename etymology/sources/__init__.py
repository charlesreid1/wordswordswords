"""
Etymology source plugins and source chaining.
"""
import logging
from typing import List, Optional, Dict

from etymology.sources.base import EtymologySource

logger = logging.getLogger(__name__)


class SourceChain:
    """Tries multiple etymology sources in priority order until one succeeds."""

    def __init__(self, sources: List[EtymologySource]):
        self.sources = sources

    def lookup(self, word: str) -> Optional[Dict]:
        """Look up a word using sources in priority order.

        Returns the first successful result, or None if all sources fail.
        """
        for source in self.sources:
            if not source.available():
                continue
            try:
                result = source.lookup(word)
                if result and result.get('root_language'):
                    result['source'] = source.name
                    return result
            except Exception as e:
                logger.warning("Source '%s' failed for '%s': %s", source.name, word, e)
                continue
        return None
