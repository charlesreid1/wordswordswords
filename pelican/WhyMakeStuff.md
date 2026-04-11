# What does make_stuff.py do?

## TL;DR
`make_stuff.py` is a **template generator script** that automates the creation of Pelican templates for a website that displays color-coded etymological analysis of literary works. It bridges between raw chapter HTML files and Pelican's templating system.

## The Big Picture

This is part of a Pelican static site generator project called **"Words Words Words"** - a website that shows color-coded word origins (Old English, French, Latin, etc.) in literary works like Ulysses, Frankenstein, Crime and Punishment, etc.

## What It Actually Does

### 1. **Reads Book Metadata**
- Loads `books.yaml` (9 books with titles, authors, short codes)
- Example: `ulysses: {title: Ulysses, author: James Joyce, short: jjul}`

### 2. **Finds Chapter Files**
- Scans `_includes/` directory for files like `ulysses1.html`, `frankenstein2.html`, etc.
- Extracts chapter numbers and titles from the HTML
- Sorts chapters numerically

### 3. **Generates Jinja2 Templates**
For each book:
- **Chapter templates** (e.g., `jjul1.html`): Wraps chapter HTML in `bookbase.html` template
- **Index template** (e.g., `jjul.html`): Creates navigation page listing all chapters

### 4. **Creates Pelican Configuration**
- Generates `template_pages.py` with `TEMPLATE_PAGES` dictionary
- Maps templates to output URLs:
  - `'ulysses/jjul.html'` → `'ulysses/index.html'`
  - `'ulysses/jjul1.html'` → `'ulysses/1/index.html'`
  - etc.

### 5. **Builds Book Listing**
- Creates `_includes/books.html` with buttons linking to each book

## Why This Script Exists (The "WTF" Part)

Without `make_stuff.py`, you'd have to manually:
- Create 100+ template files (9 books × ~15 chapters each)
- Write a massive `TEMPLATE_PAGES` dictionary by hand
- Update everything when new books/chapters are added
- Maintain consistency across all books

The script **automates all this tedious work**, making the system scalable. It's the glue between:
1. **External etymology processor** → Creates color-tagged HTML
2. **Pelican static site generator** → Builds the website

## File Relationships

```
books.yaml (metadata)
     ↓
make_stuff.py (processor)
     ↓
generated_templates/ (Jinja2 templates)
template_pages.py (URL mappings)
     ↓
pelicanconf.py (imports template_pages.py)
     ↓
Pelican → Static website
```

## The Output

Running the script creates:
- `generated_templates/` directory with organized templates
- `template_pages.py` (~70KB file with all URL mappings)
- Updated `books.html` include file

Then when Pelican builds the site, you get:
- `/ulysses/` - Book index page
- `/ulysses/1/` - Chapter 1 with color-coded words
- `/ulysses/2/` - Chapter 2
- etc.

## In Short

`make_stuff.py` **automates template generation** for a complex literary analysis website, turning raw chapter HTML into a fully navigable Pelican site with minimal manual work.