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

TEMPLATE_PAGES = {'blog.html':'blog.html',
                  'books.html':'books.html'}



EXTRA_TEMPLATES_PATHS = ['dubliners',
                         'ulysses',
                         'frankenstein',
                         'crimeandpunishment',
                         'roughingit',
                         'variableman']

# james joyce - dubliners 
TEMPLATE_PAGES['jjdu.html'] = 'dubliners/index.html'
for im1 in range(15):
    i = im1+1
    key = 'jjdu%d.html'%(i)
    val = 'dubliners/%d/index.html'%(i)
    TEMPLATE_PAGES[key] = val

# james joyce - ulysses
TEMPLATE_PAGES['jjul.html'] = 'ulysses/index.html'
for im1 in range(18):
    i = im1+1
    key = 'jjul%d.html'%(i)
    val = 'ulysses/%d/index.html'%(i)
    TEMPLATE_PAGES[key] = val

# mary shelley - frankenstein
TEMPLATE_PAGES['msfr.html'] = 'frankenstein/index.html'
for im1 in range(28):
    i = im1+1
    key = 'msfr%d.html'%(i)
    val = 'frankenstein/%d/index.html'%(i)
    TEMPLATE_PAGES[key] = val

# dostoyevsky - crime and punishment
TEMPLATE_PAGES['fdcp.html'] = 'crimeandpunishment/index.html'
for im1 in range(47):
    i = im1+1
    key = 'fdcp%d.html'%(i)
    val = 'crimeandpunishment/%d/index.html'%(i)
    TEMPLATE_PAGES[key] = val

# mark twain - roughing it
TEMPLATE_PAGES['mtri.html'] = 'roughingit/index.html'
for im1 in range(83):
    i = im1+1
    key = 'mtri%d.html'%(i)
    val = 'roughingit/%d/index.html'%(i)
    TEMPLATE_PAGES[key] = val

# philip k. dick - variable man
TEMPLATE_PAGES['pdvm.html'] = 'variableman/index.html'
for im1 in range(4):
    i = im1+1
    key = 'pdvm%d.html'%(i)
    val = 'variableman/%d/index.html'%(i)
    TEMPLATE_PAGES[key] = val


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
