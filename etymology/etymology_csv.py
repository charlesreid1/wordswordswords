from textblob import TextBlob, Word
import mechanize
from bs4 import BeautifulSoup
import pandas as pd
import re
import logging
import time
import os.path
import numpy as np
from etymology.languages import languages, languages_key

logger = logging.getLogger(__name__)


class EtymologyCSV(object):
    """
    Step 1: Gutenberg HTML -> Etymology CSV

    This class is for making a CSV file containing etymological information
    like root languages. The original text is parsed using BeautifulSoup.
    The word list is constructed using TextBlob. The etymology information
    is obtained using Mechanize and the Online Etymology Dictionary.
    The whole thing is dumped to a final CSV file.
    """

    ETYMOLOGY_KEYS = ['root word', 'root language', 'second language', 'ranked languages']

    def __init__(self, name_, do_definitions=False):
        """
        A very abbreviated setup

        name_  : single name for input/output/log files

        html file is gutenberg/<name>.html
        csv file is csv_<name>_words.csv
        log file is <name>.log
        """
        self.html_file = "gutenberg/" + name_ + ".html"
        self.words_csv_file = "csv/" + name_ + "_words.csv"
        self.etymologies_csv_file = "csv/" + name_ + "_etymologies.csv"
        self.log_file = "log/" + name_ + ".log"
        self.master_csv_file = "csv/master.csv"

        self.do_definitions = False



    def export_csv(self):
        self.export_word_file()
        self.export_rootlang_file()



    def update_master_csv(self):
        try:
            words = pd.read_csv(self.etymologies_csv_file)
        except FileNotFoundError:
            raise Exception("Error: cannot update master csv without an etymologies file: " + self.etymologies_csv_file)

        master_words = pd.read_csv(self.master_csv_file)

        words.fillna('', inplace=True)
        master_words.fillna('', inplace=True)

        new_rows = []
        for rr, word_row in words.iterrows():
            this_word = word_row['word']
            if this_word not in master_words['word'].values:
                if word_row['root language'] != '':
                    d = {}
                    for key in self.ETYMOLOGY_KEYS:
                        d[key] = words.loc[rr, key]
                    new_rows.append(d)

        if new_rows:
            master_words = pd.concat([master_words, pd.DataFrame(new_rows)], ignore_index=True)

        master_words.to_csv(self.master_csv_file, na_rep="", index=False)


    def get_root_word(self, the_word):

        logger.info("Looking for roots of %s...", the_word)

        # pick out synonyms from the synset that are basically the same word (share first 3 letters)
        try:
            full_synset = Word(the_word).synsets
            full_synset_strings = [syn.name().split('.')[0] for syn in full_synset]
        except Exception:
            full_synset_strings = []

        # only keep the suggested synset
        # if the first three letters of the synset
        # match the first three letters of the original word
        synset = []
        for sss in full_synset_strings:
            if sss[:3] == the_word[:3]:
                synset.append(sss)


        # first try removing any common suffixes
        if len(the_word) > 4:

            # -ed
            if the_word[-2:] == 'ed':

                # -XXed to -X
                # wrapped to wrap, begged to beg
                if the_word[-4] == the_word[-3]:
                    synset.insert(0, the_word[:-3])

                # -ied
                # occupied to occupy
                elif the_word[-3:] == 'ied':
                    synset.insert(0, the_word[:-3] + "y")

                else:

                    # -ed to -
                    # consonant, more likely, so prepend
                    synset.insert(0, the_word[:-2])

                    # -ed to -e
                    # tired to tire
                    synset.append(the_word[:-1])

            # -en
            if the_word[-2:] == 'en':
                # -en to -
                # quicken to quick
                synset.insert(0, the_word[:-2])

                # -en to -e
                # shaven to shave
                synset.append(the_word[:-1])

            if the_word[-2:] == 'er':
                # -er to -
                # thicker to thick
                synset.insert(0, the_word[:-2])

                # -er to -e
                # shaver to shave
                synset.append(the_word[:-1])

            # -est
            if the_word[-3:] == 'est':
                # -est to -
                # brightest to bright
                synset.insert(0, the_word[:-3])

                # -est to -e
                # widest to wide
                synset.append(the_word[:-2])

            # -ing
            if the_word[-3:] == 'ing':
                # -ing to -
                synset.insert(0, the_word[:-3])
                # -gging to -g
                # -nning to -n
                synset.append(the_word[:-4])
                # -ing to -e
                synset.append(the_word[:-3] + "e")

            # -ly
            if the_word[-2:] == 'ly':
                # -ly to -
                synset.insert(0, the_word[:-2])


        # end if len>4


        # -s/-es
        if the_word[-1:] == 's':

            # -liness
            if len(the_word) > 6:
                if the_word[-6:] == 'liness':
                    # -liness to -
                    # friendliness to friend
                    synset.insert(0, the_word[:-6])

                # -iness
                elif the_word[-5:] == 'iness':
                    # -iness to -y
                    # happiness to happy
                    synset.insert(0, the_word[:-5] + "y")

            # -ies
            # -es
            if the_word[-2:] == 'es':
                if the_word[-3:] == 'ies':
                    # -ies to -y
                    synset.insert(0, the_word[:-3] + "y")
                else:
                    # -es to -
                    synset.insert(0, the_word[:-2])
                    # -es to -e
                    synset.append(the_word[:-1])

            # -s to -
            else:
                synset.insert(0, the_word[:-1])


        if len(the_word) > 5:
            if the_word[-5:] == 'ation':
                # -ation to -ate
                # accumulation to accumulate
                synset.insert(0, the_word[:-5] + "ate")


        if synset:
            logger.info("  Trying these: %s", ", ".join(synset))

        return synset




    def etymonline_lookup(self, lookup_word):
        """
        Returns a BeautifulSoup object
        containing the results of the search
        """

        browser = mechanize.Browser()
        response = browser.open('http://www.etymonline.com/')
        browser.select_form(nr=0)
        try:
            browser['search'] = lookup_word
        except TypeError:
            pass
        resp = browser.submit()
        html_doc = resp.read()
        soup = BeautifulSoup(html_doc, 'html.parser')

        return soup




    def export_word_file(self):
        """
        The first task is to load the HTML text,
        strip everything but the paragraph tags,
        read in the resulting text, and create a
        data container with words and word counts.

        We'll do the HTML tag processing with
        BeautifulSoup.

        We'll analyze the resulting text with
        a TextBlob object.
        """

        if os.path.isfile(self.words_csv_file):

            logger.info("Loading existing words CSV...")
            words = pd.read_csv(self.words_csv_file)
            assert('word' in words.columns)
            logger.info("done")

        elif os.path.isfile(self.etymologies_csv_file):

            logger.info("Loading existing etymologies CSV...")
            words = pd.read_csv(self.etymologies_csv_file)
            assert('word' in words.columns)
            logger.info("done")


        else:

            logger.info("Opening HTML...")
            with open(self.html_file, 'r', encoding='utf-8') as f:
                html_doc = f.read()
            soup = BeautifulSoup(html_doc, 'html.parser')
            logger.info("done")



            # ------
            # page text
            # <p>
            # the texttags contain the text
            logger.info("Turning HTML into text...")
            texttags_all = [tt for tt in soup.findAll('p', text=True)]
            texttags = []
            for tta in texttags_all:
                if 'class' in tta.attrs.keys():
                    if tta.attrs['class'] == 'toc':
                        continue
                texttags.append(tta)
            logger.info("len(texttags) = %d", len(texttags))

            all_text = []
            for tt in texttags:
                all_text.append(tt.string)

            s = " ".join(str(x) for x in all_text)

            t = TextBlob(s)
            logger.info("done")

            logger.info("Getting word counts...")
            wc = t.word_counts
            logger.info("done")

            rows = []

            logger.info("Populating words...")
            for the_word in wc.keys():
                the_word = the_word.lower()
                d = {}
                d['word'] = the_word
                d['word count'] = wc[the_word]
                rows.append(d)

            words = pd.DataFrame(rows)

            logger.info("done")

            logger.info("Reindex according to word count ranking...")
            words = words.sort_values(by=['word count', 'word'], ascending=[False, True])
            words.index = range(1, len(words) + 1)
            logger.info("done")


            logger.info("Exporting to file...")
            words.to_csv(self.words_csv_file, index=False, na_rep="")
            logger.info("done")



    def export_rootlang_file(self):
        """
        This method loads the word count data container
        and populates it with etymology information.
        This etymology information is obtained by
        looking up each unique word on the Online
        Etymology Dictionary and parsing the search
        results.

        Method #2 can restart.
        """

        # first, load our csv file
        logger.info("Loading words CSV...")
        try:
            words = pd.read_csv(self.words_csv_file)
        except FileNotFoundError:
            raise Exception("Error: need a words CSV file to proceed: " + self.words_csv_file)
        words.fillna('', inplace=True)
        logger.info("done")

        wordlist = list(words['word'].values)


        etymology_keys = self.ETYMOLOGY_KEYS
        for key in etymology_keys:
            if key not in words.columns:
                words[key] = ''


        # check if master word list exists
        if os.path.isfile(self.master_csv_file):

            logger.info("Populating etymology information from previous master list...")

            # populate any missing word etymology entries
            # from the master word list:
            master_words = pd.read_csv(self.master_csv_file)
            master_words.fillna('', inplace=True)

            for rr, word_row in words.iterrows():
                this_word = word_row['word']
                if this_word in master_words['word'].values:
                    for key in etymology_keys:
                        words.loc[rr, key] = master_words.loc[master_words['word'] == this_word, key].values[0]
        else:
            master_words = pd.DataFrame([])

        try:
            untagged = len([j for j in words['root language'].values if j != ''])
        except KeyError:
            untagged = 0
        logger.info("Beginning etymology lookups with 0 of %d words, %d untagged words", len(wordlist), untagged)

        for cc, word_row in words.iterrows():

            the_word = word_row['word']

            # if a word is done, don't bother looking it up.
            if 'root language' in word_row.keys():
                if word_row['root language'] != '':
                    continue

            if len(the_word) < 2:
                continue


            # First, look for the word itself.
            # If that doesn't work, try variations.

            found_result = False

            # ------------
            # Original word

            try:
                soup = self.etymonline_lookup(the_word)
            except Exception as e:
                logger.error("Failed to look up '%s': %s", the_word, e)
                continue

            matching_words = {}
            root_words = {}

            # dt = dictionary term
            dts = soup.find_all('dt')

            # dd = dictionary definition
            dds = soup.find_all('dd')

            # Look for original word
            # in each search result
            for dt, dd in zip(dts, dds):

                this_word_full = dt.get_text()

                # remove (n./adj./v.)
                # ("the" is the only word that doesn't have n/adj/v)
                if the_word != 'the':
                    this_word = this_word_full.split(' ')[0]
                    this_word = ''.join(this_word)
                else:
                    this_word = this_word_full
                this_word = this_word.strip()



                if the_word.lower() == this_word.lower():
                    # We have an exact match!

                    etym = dd.get_text()

                    matching_words[the_word] = etym
                    root_words[the_word] = the_word

                    found_result = True

                    break


            # Now check for common suffixes...
            if found_result == False:

                roots = self.get_root_word(the_word)

                # look for each root
                for root in roots:

                    try:
                        soup = self.etymonline_lookup(root)
                    except Exception as e:
                        logger.error("Failed to look up root '%s': %s", root, e)
                        continue

                    dts = soup.find_all('dt')
                    dds = soup.find_all('dd')

                    for dt, dd in zip(dts, dds):

                        this_word_full = dt.get_text()

                        this_word = this_word_full.split(' ')[0]
                        this_word = ''.join(this_word)

                        if root.lower() == this_word.lower():

                            etym = dd.get_text()

                            matching_words[the_word] = etym
                            root_words[the_word] = root

                            found_result = True

                            break


            if found_result:

                if the_word in matching_words.keys():

                    etymology = matching_words[the_word]

                    root_word = root_words[the_word]

                    # create a grid with location (in etymology) of each language's reference.
                    etymology_grid = []

                    for lang in languages:

                        m = re.search(lang + r'\b', etymology)

                        # double check if N is actually Old N
                        n = re.search('Old ' + lang + r'\b', etymology)

                        if (m and not n):
                            etymology_grid.append(m.start())
                        else:
                            # this may skip some languages, if Old ____ also appears
                            etymology_grid.append(-1)

                    # each word is tagged with whatever language
                    # is referenced FIRST in the etymology

                    etymology_grid_gt0 = [eg for eg in etymology_grid if eg >= 0]

                    if len(etymology_grid_gt0) > 0:

                        sorted_etymology_grid = sorted(etymology_grid_gt0)

                        ranked_langs = [''] * len(etymology_grid_gt0)

                        ranking = []
                        for ii, et in enumerate(etymology_grid):

                            if et >= 0:
                                val = sorted_etymology_grid.index(et)
                            else:
                                val = -1

                            ranking.append(val)

                        for i, r in enumerate(ranking):
                            if r > -1:
                                ranked_langs[r] = languages[i]
                        ranked_languages = ";".join(ranked_langs)

                        try:
                            language1_name = ranked_langs[0]
                        except IndexError:
                            language1_name = ''

                        try:
                            language2_name = ranked_langs[1]
                        except IndexError:
                            language2_name = ''

                        ranked_languages = ";".join(ranked_langs)

                        logger.info("Tagging word %d of %d: %s", cc, len(wordlist), the_word)
                        logger.info("%s : %s", the_word, language1_name)

                        etymology_info = [root_word, language1_name, language2_name, ranked_languages]
                        d = {}
                        for key, info in zip(etymology_keys, etymology_info):
                            d[key] = info
                            words.loc[cc, key] = info
                        if len(master_words) == 0:
                            master_words = pd.DataFrame([d])
                        else:
                            master_words = pd.concat([master_words, pd.DataFrame([d])], ignore_index=True)

            else:
                # no result found. mark it '' and not NaN.
                for key in etymology_keys:
                    words.loc[cc, key] = ''

            if cc % 50 == 0:
                logger.info("Exporting to file...")

                words.fillna('', inplace=True)
                words.to_csv(self.etymologies_csv_file, index=False)

                master_words.fillna('', inplace=True)
                master_words.to_csv(self.master_csv_file, index=False)

                logger.info("done")

        logger.info("Exporting to file...")
        words.fillna('', inplace=True)
        words.to_csv(self.etymologies_csv_file, na_rep="", index=False)

        master_words.fillna('', inplace=True)
        master_words.to_csv(self.master_csv_file, na_rep="", index=False)
        logger.info("done")
