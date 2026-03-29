from bs4 import BeautifulSoup
import pandas as pd
import re
import logging
import string
import os.path
from etymology.languages import languages, languages_key

logger = logging.getLogger(__name__)


class EtymologyHTML(object):
    """
    Step 2: Etymology CSV -> Etymology HTML

    This class is for turning a CSV with etymology information
    into an HTML with tagged words.
    """

    def __init__(self, name_):
        """
        Quick set up of etymology csv object.
        """
        self.gutenberg_file = "gutenberg/" + name_ + ".html"
        self.csv_file = "csv/" + name_ + "_etymologies.csv"
        self.html_file = "html/" + name_ + ".html"
        self.log_file = "log/" + name_ + ".log"
        self.temp_file = "html/temp_" + name_ + ".html"
        self.name_ = name_


    def _build_etymology_lookup(self, words_w_lang):
        """Build a dict for O(1) word->language lookups."""
        lookup = {}
        for _, row in words_w_lang.iterrows():
            word = row['word'].lower()
            full_lang = row['root language']
            if full_lang in languages_key:
                lookup[word] = languages_key[full_lang]
        return lookup


    def _tag_tokens(self, tokens, etymology_lookup):
        """Tag a list of tokens using the etymology lookup dict."""
        for i, token in enumerate(tokens):
            stripped = token.lower().strip(string.punctuation)
            if stripped in etymology_lookup:
                lang = etymology_lookup[stripped]
                tokens[i] = '<span class="' + lang + '">' + token + '</span>'
        return tokens


    def export_html_file(self):
        """
        First check if we have an HTML file underway.

        If so, add it to our list of strings,
        find our starting place, and keep going.

        If not, load the etymology data container.
        Then loop through each paragraph, and look up
        each word in our etymology data container.
        """
        words = pd.read_csv(self.csv_file)
        words = words.fillna("")

        words_w_lang = words[words['root language'] != '']

        # Build O(1) lookup dict
        etymology_lookup = self._build_etymology_lookup(words_w_lang)

        # save file locally
        with open(self.gutenberg_file, 'r', encoding='utf-8') as f:
            html_doc = f.read()

        # this is the Gutenberg text
        # (it will be modified to make our new page)
        soup = BeautifulSoup(html_doc, 'html.parser')


        # new body contains the list of
        # strings that will form our new
        # html file.
        new_body = []



        # Check if we already have html file
        # (export finished or underway)

        if os.path.isfile(self.html_file):

            # Yes, we have an existing html file
            # (finished or underway)
            with open(self.html_file, 'r', encoding='utf-8') as f:
                html_doc2 = f.read()
            soup2 = BeautifulSoup(html_doc2, 'html.parser')

            # now that we have both html docs
            # as soups... compare last <p>
            if soup.p[-1].lower() == soup2.p[-1].string.lower():
                # We are finished
                logger.info("Found a finished HTML file in %s", self.html_file)

            else:
                # We are not finished
                logger.info("Found an unfinished HTML file in %s", self.html_file)

                # Check if last paragraph is in gutenberg
                # If so, pick up at that <p> index
                gutenberg_ps = soup.findAll('p', text=True)
                gutenberg_text = [p.string.lower() for p in gutenberg_ps]

                if soup2.p[-1].string.lower() in gutenberg_text:
                    logger.info("Picking up where we left off...")
                else:
                    raise Exception("I'm lost!")




        else:

            logger.info("Tagging HTML...")
            logger.info("Be patient! Tagging %d words...", len(words_w_lang))


            # ------
            # title and author
            titletag = soup.findAll('h1', text=True)[0]
            title = titletag.string
            self.title = title

            authortag = soup.findAll('h2', text=True)[0]
            author = re.sub('By ', '', authortag.string)
            self.author = author


            # prepend some front-matter tags
            # this info will be used by Pelican
            new_body = ["<html><head><title>" + title + "</title>",
                        '<meta name="author" content="' + self.author + '" />',
                        '<meta name="save_as" content="' + self.name_ + '.html" />',
                        "</head><body>"]



            # -----
            # table of contents
            tocs = [toc for toc in soup.findAll('p', {"class": "toc"})]


            # ------
            # page text
            # <p>
            # or chapter markers
            # <h2>
            # the booktags contain the book text
            booktags = [tt for tt in soup.findAll(['p', 'h2'], text=True)]
            logger.info("len(booktags) = %d", len(booktags))

            new_body = []

            iptot = len(booktags)
            ip = 1
            ich = 1
            for booktag in booktags:


                if booktag.name == 'h2':

                    # skip first and second ones - both are author
                    if ich == 1 or ich == 2:
                        ich += 1
                        pass

                    logger.info("Tagging chapter heading %d", ich)

                    # dump everything we have so far, first
                    if ich % 2 == 0:
                        logger.info("Making some backup soup")
                        soup_backup = BeautifulSoup(' '.join(new_body), 'html.parser')
                        with open(self.html_file, 'w', encoding='utf-8') as f:
                            f.write(soup_backup.prettify())
                        logger.info("done")


                    ich += 1

                    new_body.append(str(booktag))



                elif booktag.name == 'p':

                    if ip % 5 == 0:
                        logger.info("Tagging paragraph %d of %d", ip, iptot)

                    ip += 1

                    if booktag.string is not None:

                        split = booktag.string.split()
                        split = self._tag_tokens(split, etymology_lookup)
                        new_ptag_html = ' '.join(split)

                        new_body.append("<p>" + new_ptag_html + "</p>")

            # finish up the tags
            new_body.append("</body></html>")

            logger.info("done")

            logger.info("Making some soup")
            soup = BeautifulSoup(' '.join(new_body), 'html.parser')
            logger.info("done")


        logger.info("Writing to file %s", self.html_file)
        with open(self.html_file, 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        logger.info("done")
