Title: Words, Words, Words.
Date: 2010-12-03 10:20
Modified: 2010-12-05 19:30
Authors: charlesreid1
HeaderStyle: jumbotron
URL: 
save_as: index.html

## What does it do?

Words Words Words is a project using Python to color-code words in text
according to their etymological roots, and render the result as HTML.

The output of the scripts is available in the book list on the right.
The repository contains the scripts used to mark up the text, 
look words up in the Online Etymology Dictionary and parse the results
to tag words with their root language, and create the final HTML.

The tool is entirely implemented in Python.

## What books are available?

All of the books that have been tagged are listed on the right. 
More books are on the way...

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
* To generate color palettes for various languages, I used [The Color Brewer](http://colorbrewer2.org/)

## Who wrote Words Words Words?

Charles Reid wrote Words Words Words.

Visit [charlesreid1.com](http://charlesreid1.com/)

or check out [@charlesreid1 on Github](https://github.com/charlesreid1)

## Check out the code

The code for Words Words Words is on Github:

<a class="btn btn-success" href="http://github.com/charlesreid1/wordswordswords" role="button">Words Words Words on Github</a>

