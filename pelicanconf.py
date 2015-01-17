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


PLUGIN_PATHS = ['/home/charles/codes/pelican-plugins/']
#PLUGINS = ['liquid_tags.include_code','liquid_tags.include_html']
PLUGINS = ['liquid_tags','liquid_tags.include_code','liquid_tags.include_html']


# directory for include_code
CODE_DIR = 'code'

# directory for include_html
BOOKS_DIR = 'html'

STATIC_PATHS = ['images','code']# don't need 'html' or original files because we're copying the html into the final page 




THEME = 'cmr-pelican-theme'
DISPLAY_PAGES_ON_MENU = False
#ADDITIONAL_CSS_FILE = 'wordswordswords.css'

# dark and pastels.
BOOTSWATCH_THEME = 'darkly'


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
