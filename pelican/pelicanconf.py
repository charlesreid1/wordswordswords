#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'charlesreid1'
SITENAME = u'Words Words Words'
SITEURL = '/wordswordswords'

PATH = 'content'

TIMEZONE = 'America/Los_Angeles'

DEFAULT_LANG = u'en'




# --------------8<---------------------


# Don't try to turn HTML files into pages
READERS = {'html': None}


#PLUGIN_PATHS = ['/Users/charles/codes/pelican-plugins/']
#PLUGIN_PATHS = ['/home/charles/codes/pelican-plugins/']


# directory for include_code
CODE_DIR = 'code'

# directory for include_html
BOOKS_DIR = 'html'

STATIC_PATHS = ['images','code']




THEME = 'cmr-pelican-theme'
DISPLAY_PAGES_ON_MENU = False
#ADDITIONAL_CSS_FILE = 'wordswordswords.css'

# dark and pastels.
BOOTSWATCH_THEME = 'darkly'




DIRECT_TEMPLATES = ('index', 'archives','books','blog')

# Standard directories for templates
THEME_TEMPLATES_OVERRIDES = [
    'generated_templates'
]

import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from template_pages import TEMPLATE_PAGES
    print(f"DEBUG: Loaded TEMPLATE_PAGES with {len(TEMPLATE_PAGES)} entries")
except ImportError as e:
    TEMPLATE_PAGES = {'blog.html':'blog.html', 'books.html':'books.html'}
    print(f"DEBUG: Using default TEMPLATE_PAGES with {len(TEMPLATE_PAGES)} entries")
    print(f"DEBUG: Import error: {e}")


# --------------8<---------------------





# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

DEFAULT_PAGINATION = False

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True
