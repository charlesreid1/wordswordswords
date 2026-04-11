import os
import glob
import re
import yaml
from bs4 import BeautifulSoup

TEMPLATE_WRAPPER = """{% extends 'bookbase.html' %}
{% block title %}{title} &mdash; {{ SITENAME }}{% endblock %}
{% block content %}

{% include '_includes/{filename}' %}

{% endblock %}
"""

INDEX_WRAPPER = """{% extends 'base.html' %}
{% block title %}{title} &mdash; {{ SITENAME }}{% endblock %}
{% block content %}

<h1>{title}</h1>
<h2>{author}</h2>

<p>&nbsp;</p>
<hr />
<p>&nbsp;</p>

{links}

{% endblock %}
"""

def extract_chapter_title(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
            h2 = soup.find('h2')
            if h2 and h2.text:
                return h2.text.strip()
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
    return ""

def get_chapters(book_name):
    """Globs the _includes directory for chapters of the given book."""
    include_dir = os.path.join("cmr-pelican-theme", "templates", "_includes")
    # Matches files like frankenstein1.html, frankenstein2.html
    pattern = os.path.join(include_dir, f"{book_name}[0-9]*.html")
    files = glob.glob(pattern)
    
    # Sort them numerically
    def extract_num(filepath):
        basename = os.path.basename(filepath)
        match = re.search(r'\d+', basename)
        return int(match.group()) if match else 0
        
    files.sort(key=extract_num)
    
    chapters = []
    for f in files:
        num = extract_num(f)
        title = extract_chapter_title(f)
        if not title:
            title = f"Chapter {num}"
        chapters.append((num, title))
        
    return chapters

def make_book_templates(book_name, data, chapters):
    base_dir = os.path.join('generated_templates', book_name)
    os.makedirs(base_dir, exist_ok=True)
    
    # Chapter templates
    for num, _ in chapters:
        templatename = os.path.join(base_dir, f"{data['short']}{num}.html")
        filename = f"{book_name}{num}.html"
        
        with open(templatename, 'w') as f:
            f.write(TEMPLATE_WRAPPER.format(title=data['title'], filename=filename))
            
    # Index template
    links = []
    for num, chapter_name in chapters:
        link = f'<p><a class="btn btn-large btn-primary" href="{num}/index.html">{num} &mdash; {chapter_name}</a></p>'
        links.append(link)
        
    indexname = os.path.join(base_dir, f"{data['short']}.html")
    with open(indexname, 'w') as f:
        f.write(INDEX_WRAPPER.format(
            title=data['title'], 
            author=data['author'], 
            links='\n'.join(links)
        ))

def generate_pelican_config_snippet(books_data):
    snippet = []
    snippet.append("# --- AUTO-GENERATED TEMPLATE PAGES ---")
    snippet.append("TEMPLATE_PAGES = {'blog.html':'blog.html', 'books.html':'books.html'}")
    
    for book_name, data in books_data.items():
        short = data['short']
        snippet.append(f"\n# {data['title']}")
        # Book index page at /bookname/index.html
        snippet.append(f"TEMPLATE_PAGES['{short}.html'] = '{book_name}/index.html'")
        
        # We need the chapters to generate the snippet properly
        chapters = get_chapters(book_name)
        for num, _ in chapters:
            # Chapter pages at /bookname/num/index.html
            snippet.append(f"TEMPLATE_PAGES['{short}{num}.html'] = '{book_name}/{num}/index.html'")
            
    return '\n'.join(snippet)

def generate_books_include(books_data):
    """Generates the _includes/books.html file dynamically."""
    output_path = os.path.join("cmr-pelican-theme", "templates", "_includes", "books.html")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    html = ['<div class="well">\n <div>\n  <p>\n   <h1>\n    Tagged Books\n   </h1>\n  </p>']
    
    for book_name, data in books_data.items():
        title = data['title']
        author = data['author']
        
        # Link to the book's index page folder
        html.append(f'  <p>\n   <h2>\n    {title}, by {author}\n   </h2>\n   <a class="btn btn-large btn-success" href="{book_name}">\n    See this book\'s etymology\n    <i class="fa fa-arrow-circle-o-right">\n    </i>\n   </a>\n  </p>')
        
    html.append(' </div>\n</div>')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html))

if __name__ == "__main__":
    # Load books from yaml
    try:
        # Check if we are in pelican/ or root
        yaml_path = '../books.yaml' if os.path.exists('../books.yaml') else 'books.yaml'
        with open(yaml_path, 'r') as f:
            BOOKS = yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading books.yaml: {e}")
        BOOKS = {}

    if not BOOKS:
        print("No books found. Exiting.")
        exit(1)

    for book_name, data in BOOKS.items():
        print(f"Generating templates for {book_name}...")
        chapters = get_chapters(book_name)
        if not chapters:
            print(f"  Warning: No chapters found for {book_name}. Ensure etymology step has run.")
        else:
            print(f"  Found {len(chapters)} chapters.")
        make_book_templates(book_name, data, chapters)
        
    print("Generating books.html include...")
    generate_books_include(BOOKS)
        
    print("Writing template_pages.py...")
    with open("template_pages.py", 'w') as f:
        f.write(generate_pelican_config_snippet(BOOKS))
    
    print("\nDone!")
