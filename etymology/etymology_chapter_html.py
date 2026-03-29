from bs4 import BeautifulSoup
import pandas as pd
import re
import logging
import os.path
from etymology.etymology_html import EtymologyHTML

logger = logging.getLogger(__name__)


class EtymologyChapterHTML(EtymologyHTML):
    """
    Step 2: Etymology CSV -> Etymology HTML

    This class is for turning a CSV with etymology information
    into an HTML with tagged words, one file per chapter.
    """

    def export_html_file(self):
        """
        Load the etymology data container.
        Then loop through each paragraph, and look up
        each word in our etymology data container.
        """
        self.dest_dir = "html"

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


        h2tags = [tt for tt in soup.findAll('h2', text=True)]
        h2tags = h2tags[1:]

        ich = 1
        for h2tag in h2tags:

            logger.info("Tagging chapter heading %d", ich)

            new_body = []

            new_body.append(str(h2tag))

            chapter_file = self.name_ + str(ich) + ".html"

            nexttag = h2tag.findNextSibling(['p', 'h2'])
            if nexttag is None:
                break

            ip = 0
            while True:

                if nexttag.name == 'h2':
                    break
                if nexttag is None:
                    break

                ip += 1
                if ip % 25 == 0:
                    logger.info("Paragraph %d", ip)

                try:
                    split = nexttag.string.split()
                except AttributeError:
                    split = []

                if split:
                    split = self._tag_tokens(split, etymology_lookup)
                    new_html = ' '.join(split)
                    new_body.append(new_html)

                nexttag = nexttag.findNextSibling(['p', 'h2'])
                if nexttag is None:
                    break


            logger.info("done with chapter")

            logger.info("Making some soup")
            chapter_soup = BeautifulSoup(' '.join(new_body), 'html.parser')
            logger.info("done")

            logger.info("Writing to file %s", chapter_file)
            with open(self.dest_dir + "/" + chapter_file, 'w', encoding='utf-8') as f:
                f.write(chapter_soup.prettify())
            logger.info("done")

            ich += 1
