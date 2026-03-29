# Words Words Words

This repo contains Python code for tagging words based on their etymology.
You can get more information from the [Words Words Words web site](http://charlesreid1.github.io/wordswordswords)
or by browsing this repository.

Finished product: [http://charlesreid1.github.io/wordswordswords](http://charlesreid1.github.io/wordswordswords)

Repository name is a reference to _Hamlet_.

## Prerequisites

- **Python 3.10+** (recommended)
- **External API Keys**: 
  - To use the LLM-based etymology lookup, you must set the `ANTHROPIC_API_KEY` environment variable.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/charlesreid1/wordswordswords.git
   cd wordswordswords
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. (Optional) Initialize the SQLite cache from existing CSV files:
   ```bash
   python -m etymology.run --migrate
   ```

## Usage

The primary way to use the library is via the `etymology.run` module.

### Running the Full Pipeline

To process a book from a Gutenberg HTML file through all stages (extraction, lookup, and generation):

```bash
python -m etymology.run --book <book_name> --step all
```

The `<book_name>` corresponds to the filename in the `gutenberg/` directory (e.g., `frankenstein`).

### Pipeline Stages

You can also run individual steps of the pipeline:

- **Extract**: Process the raw Gutenberg HTML and generate a word frequency list.
  ```bash
  python -m etymology.run --book <book_name> --step extract
  ```
- **Lookup**: Fetch etymological data for the word list using configured sources (Wiktionary, Etymonline, LLM). Results are cached in `data/etymologies.db`.
  ```bash
  python -m etymology.run --book <book_name> --step lookup
  ```
- **Generate**: Create the final tagged HTML file where recognized words are wrapped in `<span class='language'>` tags.
  ```bash
  python -m etymology.run --book <book_name> --step generate
  ```

### Legacy Mode

The library also supports its original execution mode:

```bash
python -m etymology.run --mode legacy --book <book_name> --step all
```

## Configuration

The pipeline's behavior can be customized in `etymology/config.yaml`:

- **Sources**: Choose the order of etymology lookup sources (`wiktionary`, `etymonline`, `llm`).
- **WordNet Lemmatization**: Enable/disable lemmatization before looking up a word's etymology.
- **Rate Limits**: Configure delay between requests for external sources.
- **LLM Settings**: Specify which model to use for LLM-based lookup.

## Project Structure

- `etymology/`: Main Python package containing the core logic.
- `gutenberg/`: Input HTML files from Project Gutenberg.
- `csv/`: Intermediate word lists and legacy CSV etymology data.
- `data/`: SQLite cache and progress tracking files.
- `html/`: Generated tagged HTML files.
- `pelican/`: Configuration for generating the static web site.
