import os

BOOKS = {
    'dubliners': {
        'title': 'Dubliners',
        'author': 'James Joyce',
        'short': 'jjdu',
        'chapters': [
            'The Sisters', 'An Encounter', 'Araby', 'Eveline', 'After the Race',
            'Two Gallants', 'The Boarding House', 'A Little Cloud', 'Counterparts',
            'Clay', 'A Painful Case', 'Ivy Day in the Committee Room', 'A Mother',
            'Grace', 'The Dead'
        ]
    },
    'ulysses': {
        'title': 'Ulysses',
        'author': 'James Joyce',
        'short': 'jjul',
        'chapters': [
            'Telemachus', 'Nestor', 'Proteus', 'Calypso', 'Lotus Eaters',
            'Hades', 'Aeolus', 'Lestrygonians', 'Scylla and Charybdis',
            'Wandering Rocks', 'Sirens', 'Cyclops', 'Nausicaa',
            'Oxen of the Sun', 'Circe', 'Eumaeus', 'Ithaca', 'Penelope'
        ]
    },
    'frankenstein': {
        'title': 'Frankenstein',
        'author': 'Mary Shelley',
        'short': 'msfr',
        'chapters': [f"Chapter {i+1}" for i in range(28)]
    },
    'crimeandpunishment': {
        'title': 'Crime and Punishment',
        'author': 'Fyodor Dostoyevsky',
        'short': 'fdcp',
        'chapters': [f"Chapter {i+1}" for i in range(47)]
    },
    'roughingit': {
        'title': 'Roughing It',
        'author': 'Mark Twain',
        'short': 'mtri',
        'chapters': [f"Chapter {i+1}" for i in range(83)]
    },
    'variableman': {
        'title': 'The Variable Man',
        'author': 'Philip K. Dick',
        'short': 'pdvm',
        'chapters': [f"Chapter {i+1}" for i in range(4)]
    },
    'leviathan': {
        'title': 'Leviathan',
        'author': 'Thomas Hobbes',
        'short': 'thle',
        'chapters': [f"Chapter {i+1}" for i in range(73)]
    }
}

TEMPLATE_WRAPPER = """{{% extends 'bookbase.html' %}}
{{% block title %}}{title} &mdash; {{{{ SITENAME }}}}{{% endblock %}}
{{% block content %}}

{{% include '_includes/{filename}' %}}

{{% endblock %}}
"""

INDEX_WRAPPER = """{{% extends 'base.html' %}}
{{% block title %}}{title} &mdash; {{{{ SITENAME }}}}{{% endblock %}}
{{% block content %}}

<h1>{title}</h1>
<h2>{author}</h2>

<p>&nbsp;</p>
<hr />
<p>&nbsp;</p>

{links}

{{% endblock %}}
"""

def make_book_templates(book_name, data):
    os.makedirs(book_name, exist_ok=True)
    
    # Chapter templates
    for i, _ in enumerate(data['chapters']):
        ich = i + 1
        templatename = os.path.join(book_name, f"{data['short']}{ich}.html")
        filename = f"{book_name}{ich}.html"
        
        with open(templatename, 'w') as f:
            f.write(TEMPLATE_WRAPPER.format(title=data['title'], filename=filename))
            
    # Index template
    links = []
    for i, chapter_name in enumerate(data['chapters']):
        ich = i + 1
        link = f'<p><a class="btn btn-large btn-primary" href="{ich}/index.html">{ich} &mdash; {chapter_name}</a></p>'
        links.append(link)
        
    indexname = os.path.join(book_name, f"{data['short']}.html")
    with open(indexname, 'w') as f:
        f.write(INDEX_WRAPPER.format(
            title=data['title'], 
            author=data['author'], 
            links='\n'.join(links)
        ))

def generate_pelican_config_snippet():
    snippet = []
    snippet.append("# --- AUTO-GENERATED TEMPLATE PAGES ---")
    snippet.append("TEMPLATE_PAGES = {'blog.html':'blog.html', 'books.html':'books.html'}")
    
    for book_name, data in BOOKS.items():
        short = data['short']
        snippet.append(f"\n# {data['title']}")
        snippet.append(f"TEMPLATE_PAGES['{short}.html'] = '{book_name}/{short}.html'")
        for i in range(len(data['chapters'])):
            ich = i + 1
            snippet.append(f"TEMPLATE_PAGES['{short}{ich}.html'] = '{book_name}/{ich}/index.html'")
            
    return '\n'.join(snippet)

if __name__ == "__main__":
    for book_name, data in BOOKS.items():
        print(f"Generating templates for {book_name}...")
        make_book_templates(book_name, data)
        
    print("Writing template_pages.py...")
    with open("template_pages.py", 'w') as f:
        f.write(generate_pelican_config_snippet())
    
    print("\nDone!")
