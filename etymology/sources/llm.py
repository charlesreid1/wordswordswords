"""
LLM-based etymology source using the Claude API.

Last-resort fallback for words that no other source can resolve.
Batches multiple words per API call to reduce cost.
Requires ANTHROPIC_API_KEY environment variable.
"""
import json
import logging
import os
from typing import Optional, Dict, List

from etymology.sources.base import EtymologySource
from etymology.languages import languages

logger = logging.getLogger(__name__)

LANGUAGES_LIST = ", ".join(languages)

SYSTEM_PROMPT = """You are an expert etymologist. When given an English word, identify its primary etymological origin language. Be precise and scholarly. Only use languages from this list: """ + LANGUAGES_LIST

SINGLE_PROMPT_TEMPLATE = """For the English word "{word}", identify its etymological origin.

Return ONLY a JSON object with these exact keys:
{{
    "root_language": "<primary origin language from the allowed list>",
    "second_language": "<secondary origin language, or empty string>",
    "ranked_languages": "<semicolon-separated list of all origin languages in order>"
}}

Allowed languages: {languages}

If you cannot determine the etymology, return empty strings for all fields."""

BATCH_PROMPT_TEMPLATE = """For each of the following English words, identify its etymological origin.

Words: {words}

Return ONLY a JSON array where each element is an object with these keys:
{{
    "word": "<the word>",
    "root_language": "<primary origin language from the allowed list>",
    "second_language": "<secondary origin language, or empty string>",
    "ranked_languages": "<semicolon-separated list of all origin languages in order>"
}}

Allowed languages: {languages}

If you cannot determine the etymology for a word, use empty strings for all language fields."""


class LLMSource(EtymologySource):
    """Etymology source using Claude API as a fallback."""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-6"):
        self._api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        self._model = model
        self._client = None

    @property
    def name(self) -> str:
        return "llm"

    def available(self) -> bool:
        return self._api_key is not None

    def _get_client(self):
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self._api_key)
            except ImportError:
                logger.error("anthropic package not installed")
                return None
        return self._client

    def lookup(self, word: str) -> Optional[Dict]:
        """Look up a single word's etymology via Claude."""
        client = self._get_client()
        if client is None:
            return None

        prompt = SINGLE_PROMPT_TEMPLATE.format(word=word, languages=LANGUAGES_LIST)

        try:
            message = client.messages.create(
                model=self._model,
                max_tokens=256,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )

            text = message.content[0].text.strip()

            # Parse JSON from response (handle markdown code blocks)
            if text.startswith('```'):
                text = text.split('\n', 1)[1].rsplit('```', 1)[0].strip()

            data = json.loads(text)

            if not data.get('root_language'):
                return None

            # Validate against known languages
            if data['root_language'] not in languages:
                logger.warning("LLM returned unknown language '%s' for '%s'",
                               data['root_language'], word)
                return None

            return {
                'root_word': word,
                'root_language': data['root_language'],
                'second_language': data.get('second_language', ''),
                'ranked_languages': data.get('ranked_languages', ''),
                'raw_text': f'[LLM etymology: {text}]',
            }

        except json.JSONDecodeError as e:
            logger.error("Failed to parse LLM response for '%s': %s", word, e)
            return None
        except Exception as e:
            logger.error("LLM lookup failed for '%s': %s", word, e)
            return None

    def lookup_batch(self, words: List[str]) -> Dict[str, Optional[Dict]]:
        """Look up multiple words in a single API call.

        More cost-effective than individual lookups.
        Returns dict mapping word -> result dict (or None).
        """
        client = self._get_client()
        if client is None:
            return {w: None for w in words}

        # Batch in groups of 20 to keep prompt size manageable
        results = {}
        for i in range(0, len(words), 20):
            batch = words[i:i+20]
            batch_results = self._lookup_batch_chunk(client, batch)
            results.update(batch_results)

        return results

    def _lookup_batch_chunk(self, client, words: List[str]) -> Dict[str, Optional[Dict]]:
        """Process a single batch of up to 20 words."""
        words_str = ", ".join(f'"{w}"' for w in words)
        prompt = BATCH_PROMPT_TEMPLATE.format(words=words_str, languages=LANGUAGES_LIST)

        try:
            message = client.messages.create(
                model=self._model,
                max_tokens=2048,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )

            text = message.content[0].text.strip()

            if text.startswith('```'):
                text = text.split('\n', 1)[1].rsplit('```', 1)[0].strip()

            entries = json.loads(text)

            results = {}
            for entry in entries:
                word = entry.get('word', '').lower()
                if not word or not entry.get('root_language'):
                    results[word] = None
                    continue

                if entry['root_language'] not in languages:
                    results[word] = None
                    continue

                results[word] = {
                    'root_word': word,
                    'root_language': entry['root_language'],
                    'second_language': entry.get('second_language', ''),
                    'ranked_languages': entry.get('ranked_languages', ''),
                    'raw_text': f'[LLM etymology batch]',
                }

            # Fill in any missing words
            for w in words:
                if w.lower() not in results:
                    results[w.lower()] = None

            return results

        except Exception as e:
            logger.error("Batch LLM lookup failed: %s", e)
            return {w.lower(): None for w in words}
