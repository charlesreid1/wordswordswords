# Words Words Words — Modernization & Scaling Plan

## Context

This project analyzes classic literary texts from Project Gutenberg, looks up the etymology of every word by scraping etymonline.com, and generates color-coded HTML showing word origins by language. The codebase is Python 2, has no tests, no dependency management, several bugs, and relies entirely on fragile web scraping with no rate limiting. The goal is to (1) fix and modernize the existing code, (2) restructure it for efficiency and scalability, and (3) expand beyond scraping a single website.

**Naming convention:** All new Python files use `snake_case`. Existing CamelCase files (`EtymologyCSV.py`, `EtymologyHTML.py`, `EtymologyChapterHTML.py`) will be renamed to `etymology_csv.py`, `etymology_html.py`, `etymology_chapter_html.py` as part of Phase 1. The `Make*.py` entry points (`MakeCopperfield.py`, etc.) will be replaced by a single `run.py` CLI and can be deleted.

---

## Phase 1: Core Improvements (Fix What Exists)

### 1.1 — Add `requirements.txt`
- **File:** `requirements.txt` (new)
- Contents: `mechanize`, `beautifulsoup4`, `pandas`, `textblob`, `numpy`
- **Verify:** `pip install -r requirements.txt` in a fresh Python 3 venv

### 1.2 — Rename files to snake_case
- `etymology/EtymologyCSV.py` → `etymology/etymology_csv.py`
- `etymology/EtymologyHTML.py` → `etymology/etymology_html.py`
- `etymology/EtymologyChapterHTML.py` → `etymology/etymology_chapter_html.py`
- `etymology/MakeCopperfield.py` → delete (replaced by `run.py` in Step 1.6)
- Same for all other `Make*.py` files
- Update all internal imports to match new filenames
- **Verify:** `git mv` each file, then confirm imports resolve

### 1.3 — Port Python 2 → Python 3
All changes are mechanical syntax fixes across the 3 renamed core files:

**`etymology/etymology_csv.py`:**
- `print` statements → `print()` function calls (~20 occurrences)
- `<>` operator → `!=` (~5 occurrences)
- `unicode(s)` → `str(s)` (line 313)
- Remove `.encode('utf-8')` where unnecessary (line 328)
- `words.append([d])` → `pd.concat([words, pd.DataFrame([d])])` (lines 343, 652)
- `words.sort(columns=...)` → `words.sort_values(by=...)` (line 348)
- `from languages import ...` → `from .languages import ...`

**`etymology/etymology_html.py`:**
- `print` statements → `print()` (~15 occurrences)
- `<>` → `!=` (lines 48, 239)
- `unicode(booktag)` → `str(booktag)` (line 196)
- File writes: use `open(..., encoding='utf-8')` instead of `.encode('utf-8')`

**`etymology/etymology_chapter_html.py`:**
- Same categories: `print`, `<>`, `unicode()`, `.encode()`

**Verify:** `python3 -m py_compile etymology/*.py` — all files compile

### 1.4 — Fix Bugs
- **`etymology_csv.py` line 295:** `tt` → `tta` (wrong loop variable), and fix the toc filter logic (`pass` → `continue`)
- **`etymology_csv.py` lines 305-310, 336-340:** Dead code referencing undefined `word` variable — delete these blocks (guarded by `self.do_definitions` which is hardcoded `False`)
- **Verify:** Run end-to-end with no `NameError`

### 1.5 — Add Error Handling & Logging
- Replace bare `except:` blocks with specific exception types
- Wire up the already-imported `logging` module: `logging.info` for progress, `logging.warning` for missed words, `logging.error` for HTTP failures
- Add try/except with retry around `mechanize.Browser()` calls
- **Files:** `etymology_csv.py`, `etymology_html.py`, `etymology_chapter_html.py`

### 1.6 — Fix Punctuation in Word Matching
- **Files:** `etymology_html.py` (line 253), `etymology_chapter_html.py` (line 148)
- Strip punctuation before comparison, preserve it in output:
  ```python
  stripped = token.lower().strip(string.punctuation)
  if stripped == word.lower():
      split[it] = f'<span class="{lang}">{token}</span>'
  ```
- **Verify:** Words followed by commas/periods now get tagged

### 1.7 — Unified CLI Entry Point
- **File:** `etymology/run.py` (new)
- `python run.py --book frankenstein --step csv|html|all`
- Replaces the 9 nearly-identical `Make*.py` scripts
- **Verify:** Produces identical output to the old Make scripts

---

## Phase 2: Scale & Efficiency

### 2.1 — SQLite Cache (Replace CSV-based master.csv)
- **File:** `etymology/cache.py` (new)
- Schema: `word TEXT PK, root_word, root_language, second_language, ranked_languages, source, lookup_date, raw_text`
- API: `get(word)`, `put(word, data)`, `has(word)`, `bulk_get(words)`
- Migration script to import existing `csv/master.csv` and all `*_etymologies.csv`
- **Why SQLite:** Zero-config, stdlib, handles 10k+ words trivially, enables indexed lookups
- **Verify:** Import master.csv → query "the" → returns "Old English"

### 2.2 — Modularize into Pipeline Stages
Refactor the monolithic classes into clear stages with defined interfaces:

```
etymology/
  pipeline/
    __init__.py
    extract.py        # Stage 1: Gutenberg HTML → word list
    lookup.py         # Stage 2: word list → etymology data (via cache + sources)
    generate.py       # Stage 3: etymology data + HTML → tagged HTML
  sources/
    __init__.py
    base.py           # Abstract base class
    etymonline.py     # Existing scraper, wrapped
  cache.py
  languages.py
  run.py
```

Each stage reads/writes well-defined intermediates. Stages can run independently — a network failure in lookup doesn't require re-running extraction.

### 2.3 — Optimize O(n×m) Word Matching → O(n)
- **Current:** For each paragraph, nested loop over all etymology words × all tokens
- **Fix:** Build a `dict` lookup once, then single-pass per paragraph:
  ```python
  etymology_lookup = {row['word'].lower(): languages_key[row['root language']] for _, row in df.iterrows()}
  for i, token in enumerate(tokens):
      lang = etymology_lookup.get(token.lower().strip(punctuation))
      if lang:
          tokens[i] = f'<span class="{lang}">{token}</span>'
  ```
- **Impact:** ~30,000× speedup per paragraph for large books like Ulysses

### 2.4 — Rate Limiting & Concurrent Lookups
- Rate limiter: minimum 2-second interval between requests to etymonline.com
- `concurrent.futures.ThreadPoolExecutor` (3-5 workers) with shared rate-limit semaphore
- **Why threads over asyncio:** mechanize is synchronous; threads are simpler here
- **Verify:** 50-word batch completes with ~2s gaps, no duplicate lookups

### 2.5 — Checkpointing & Resume
- SQLite cache provides natural checkpointing (each word persisted immediately)
- Progress tracker: `data/{book}_progress.json` with total/completed/timestamp
- Resume = re-run same command; already-cached words are skipped automatically
- **Verify:** Kill mid-lookup, restart, confirm it picks up where it left off

---

## Phase 3: Expand Etymology Sources

### 3.1 — Abstract Source Interface
- **File:** `etymology/sources/base.py`
- `EtymologySource` ABC with: `lookup(word) → dict | None`, `available() → bool`, `name → str`
- Return format: `{root_word, root_language, second_language, ranked_languages, raw_text}`

### 3.2 — Wrap Existing Etymonline Scraper
- **File:** `etymology/sources/etymonline.py`
- Port existing logic from `etymology_csv.py` into `EtymologySource` subclass
- Upgrade from `mechanize` to `requests` (better maintained, native HTTPS)
- Use `https://www.etymonline.com/search?q={word}` directly instead of form submission
- Add User-Agent header, retry with exponential backoff

### 3.3 — Wiktionary API Source (recommended primary source)
- **File:** `etymology/sources/wiktionary.py`
- Free, no auth required, CC-licensed, generous rate limits (200 req/s)
- Endpoint: `https://en.wiktionary.org/api/rest_v1/page/html/{word}`
- Parse the "Etymology" section, apply same language-detection regex
- **Best replacement for etymonline scraping** — most words are covered

### 3.4 — NLTK/WordNet Lemmatizer (improves root-word detection)
- **File:** `etymology/sources/wordnet.py`
- Replace hand-rolled suffix stripping (`get_root_word`) with `WordNetLemmatizer`
- Not an etymology source itself — a preprocessor that feeds better lemmas to other sources
- Example: "occupied" → "occupy", "running" → "run" (more reliable than regex)

### 3.5 — LLM-Based Fallback (Claude API)
- **File:** `etymology/sources/llm.py`
- Last-resort source for words no other source resolves
- Prompt: structured JSON output with root_language from the known language list
- Batch multiple words per API call to reduce cost
- Requires `ANTHROPIC_API_KEY` env var
- Cache aggressively — each result goes to SQLite immediately

### 3.6 — Source Chaining
- **File:** `etymology/sources/__init__.py`
- `SourceChain` tries sources in priority order: **Cache → Wiktionary → Etymonline → LLM**
- Config file (`etymology/config.yaml`) controls source order, rate limits, API keys
- SQLite `source` column tracks which source provided each word's data

---

## Verification Plan

| Phase | Test |
|-------|------|
| 1 | All `.py` files compile under Python 3. `run.py --book variableman --step html` produces output matching existing HTML (except newly-tagged punctuated words). |
| 2 | SQLite import matches master.csv row count. Full pipeline for variableman (small book) completes. Kill-and-resume works. HTML generation benchmarks >100× faster. |
| 3 | Disable etymonline, run Wiktionary-only — expect ~85-90% word coverage. Full source chain processes a book with mixed sources visible in SQLite `source` column. LLM source only fires for words all other sources miss. |

---

## Critical Files to Modify/Create

| File | Action |
|------|--------|
| `etymology/EtymologyCSV.py` → `etymology/etymology_csv.py` | Rename + modify (Phase 1), then refactor into `pipeline/` modules (Phase 2) |
| `etymology/EtymologyHTML.py` → `etymology/etymology_html.py` | Rename + modify (Phase 1), then refactor into `pipeline/generate.py` (Phase 2) |
| `etymology/EtymologyChapterHTML.py` → `etymology/etymology_chapter_html.py` | Rename + modify (Phase 1), then merge into `pipeline/generate.py` (Phase 2) |
| `etymology/languages.py` | Minor cleanup (Phase 1) |
| `etymology/Make*.py` | Delete after `run.py` is ready (Phase 1) |
| `requirements.txt` | New (Phase 1), extended in Phase 3 |
| `etymology/run.py` | New (Phase 1) |
| `etymology/cache.py` | New (Phase 2) |
| `etymology/pipeline/__init__.py` | New (Phase 2) |
| `etymology/pipeline/extract.py` | New (Phase 2) |
| `etymology/pipeline/lookup.py` | New (Phase 2) |
| `etymology/pipeline/generate.py` | New (Phase 2) |
| `etymology/sources/__init__.py` | New (Phase 3) |
| `etymology/sources/base.py` | New (Phase 3) |
| `etymology/sources/etymonline.py` | New (Phase 3) |
| `etymology/sources/wiktionary.py` | New (Phase 3) |
| `etymology/sources/wordnet.py` | New (Phase 3) |
| `etymology/sources/llm.py` | New (Phase 3) |
| `etymology/config.yaml` | New (Phase 3) |
