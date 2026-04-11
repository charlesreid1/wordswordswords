"""
Stage 2: word list -> etymology data via cache + sources.

Looks up each word's etymology using a chain of sources,
with caching, rate limiting, and concurrent lookups.
"""
import json
import logging
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


class RateLimiter:
    """Thread-safe rate limiter with minimum interval between calls."""

    def __init__(self, min_interval=2.0):
        self._min_interval = min_interval
        self._last_time = 0.0
        self._lock = threading.Lock()

    def wait(self):
        with self._lock:
            now = time.time()
            elapsed = now - self._last_time
            if elapsed < self._min_interval:
                time.sleep(self._min_interval - elapsed)
            self._last_time = time.time()


class LookupProgress:
    """Tracks and persists lookup progress for resume capability."""

    def __init__(self, progress_path):
        self.path = progress_path
        self.data = {'total': 0, 'completed': 0, 'last_word': '', 'completed_words': []}
        if os.path.isfile(progress_path):
            with open(progress_path, 'r') as f:
                self.data = json.load(f)

    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, 'w') as f:
            json.dump(self.data, f, indent=2)

    def mark_complete(self, word):
        self.data['completed'] += 1
        self.data['last_word'] = word
        self.data['completed_words'].append(word)
        if self.data['completed'] % 50 == 0:
            self.save()

    def is_done(self, word):
        return word in self.data.get('completed_words', [])


def lookup_words(words, cache, source_chain, max_workers=3, rate_limit=2.0,
                 progress_path=None):
    """Look up etymologies for a list of words.

    Args:
        words: List of (word, count) tuples or list of word strings.
        cache: EtymologyCache instance.
        source_chain: SourceChain instance (or any object with .lookup(word) method).
        max_workers: Number of concurrent lookup threads.
        rate_limit: Minimum seconds between requests per worker.
        progress_path: Optional path for progress tracking JSON.

    Returns:
        Dict mapping word -> etymology data dict.
    """
    # Normalize input
    if words and isinstance(words[0], tuple):
        word_list = [w for w, _ in words]
    else:
        word_list = list(words)

    # Filter out short words
    word_list = [w for w in word_list if len(w) >= 2]

    # Check cache first
    logger.info("Checking cache for %d words...", len(word_list))
    cached = cache.bulk_get(word_list)
    uncached = [w for w in word_list if w.lower() not in cached]
    logger.info("Found %d cached, %d need lookup", len(cached), len(uncached))

    # Set up progress tracking
    progress = None
    if progress_path:
        progress = LookupProgress(progress_path)
        progress.data['total'] = len(word_list)
        uncached = [w for w in uncached if not progress.is_done(w)]
        logger.info("After resume filter: %d words to look up", len(uncached))

    if not uncached:
        logger.info("All words already cached.")
        return cached

    # Rate limiter shared across threads
    limiter = RateLimiter(rate_limit)

    results = dict(cached)
    lock = threading.Lock()
    errors = []

    def _lookup_one(word):
        try:
            limiter.wait()
            result = source_chain.lookup(word)
            if result and result.get('root_language'):
                # Write to cache immediately (thread-safe via SQLite WAL)
                cache.put(word, result)
                with lock:
                    results[word.lower()] = result
                if progress:
                    progress.mark_complete(word)
                return word, result
            else:
                if progress:
                    progress.mark_complete(word)
                return word, None
        except Exception as e:
            logger.error("Error looking up '%s': %s", word, e)
            errors.append((word, str(e)))
            return word, None

    logger.info("Looking up %d words with %d workers...", len(uncached), max_workers)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_lookup_one, w): w for w in uncached}

        done_count = 0
        for future in as_completed(futures):
            word, result = future.result()
            done_count += 1
            if done_count % 50 == 0:
                logger.info("Progress: %d/%d lookups complete", done_count, len(uncached))

    if progress:
        progress.save()

    if errors:
        logger.warning("%d words failed lookup", len(errors))

    found = sum(1 for w in uncached if w.lower() in results)
    logger.info("Lookup complete. Found %d/%d uncached words.", found, len(uncached))

    return results
