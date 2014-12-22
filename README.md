wordswordswords
===============

tools for analyzing text.

## kde wordlength

Compute KDE of wordlength probability distribution.

![KDE of wordlengths for various novels.](https://raw.github.com/charlesreid1/wordswordswords/master/img/kde_wordlength.jpg)

## custom wordcount

This script loads text files from data/ and runs stats on them.

It computes a lexical complexity score, and prints the 100 most common words.

It also prints a word frequency plot.

![Screenshot of custom wordcount script in action](https://raw.github.com/charlesreid1/wordswordswords/master/img/WCScreenshot.png)

## nltk wordcount

This script loads books from nltk database/downloads. These texts are special
nltk objects, but are basically nltk.text.Text objects that are already tokenized.

