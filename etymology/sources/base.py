"""
Abstract base class for etymology data sources.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict


class EtymologySource(ABC):
    """Base class for all etymology data sources."""

    @abstractmethod
    def lookup(self, word: str) -> Optional[Dict]:
        """Look up a single word's etymology.

        Returns:
            Dict with keys: root_word, root_language, second_language,
            ranked_languages, raw_text. Or None if not found.
        """
        pass

    @abstractmethod
    def available(self) -> bool:
        """Whether this source is currently available."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable source name for logging and cache tracking."""
        pass
