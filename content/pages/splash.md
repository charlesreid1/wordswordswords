Title: Words, Words, Words.
Date: 2010-12-03 10:20
Modified: 2010-12-05 19:30
Authors: charlesreid1
HeaderStyle: jumbotron
URL: 
save_as: index.html

## What does it do?

Words Words Words is a repository containing scripts for marking up 
HTML text with colored tags indicating the root languages of words.

The tool is entirely implemented in Python.

## How does it work?

Words Words Words uses a couple of Python libraries to do its primary tasks: parse text, look up words on a web page, extract and process the result, and convert the original text into HTML, color-coding each word in the process with its etymological root language.

* To parse the text and extract unique words, I'm using the [Natural Language Toolkit](http://www.nltk.org).
* To scrape the web, I'm using [Mechanize](http://wwwsearch.sourceforge.net/mechanize/).
* To obtain etymological root languages for words, I'm using the [Online Etymology Dictionary](http://www.etymonline.com).
* To process the resulting HTML, I'm using [Beautiful Soup](http://www.crummy.com/software/BeautifulSoup/bs4/doc/).
* To deal with all the data resulting from these tasks, I'm using [Pandas](http://pandas.pydata.org/).
* To tag each word, I'm just using Python's built-in ```list``` and ```string``` types.
* To pull all of the tagged HTML, CSS stylesheets, and JS together, I'm using [Pelican](http://blog.getpelican.com/) 
  (my preferred Python alternative to Ruby's Jekyll)

## Check out the code

The code for Words Words Words is on Github:

<a class="btn btn-success" href="http://github.com/charlesreid1/wordswordswords" role="button">Words Words Words on Github</a>

