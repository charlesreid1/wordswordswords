from textblob import TextBlob, Word
import mechanize
from bs4 import BeautifulSoup
import pandas as pd
import re
import logging
import time
import os.path
import numpy as np
from languages import languages, languages_key


class EtymologyCSV(object):
    """
    Step 1: Gutenberg HTML -> Etymology CSV

    This class is for making a CSV file containing etymological information
    like root languages. The original text is parsed using BeautifulSoup.
    The word list is constructed using TextBlob. The etymology information
    is obtained using Mechanize and the Online Etymology Dictionary.
    The whole thing is dumped to a final CSV file.
    """

    def __init__(self,name_,do_definitions=False):
        """
        A very abbreviated setup

        name_  : single name for input/output/log files

        html file is gutenberg/<name>.html
        csv file is csv_<name>_words.csv
        log file is <name>.log
        """
        self.html_file = "gutenberg/"+name_+".html"
        self.words_csv_file  = "csv/"+name_+"_words.csv"
        self.etymologies_csv_file  = "csv/"+name_+"_etymologies.csv"
        self.log_file  = "log/"+name_+".log"
        self.master_csv_file = "csv/master.csv"

        self.do_definitions = False



    def export_csv(self):
        self.export_word_file()
        self.export_rootlang_file()



    def update_master_csv(self):
        try:
            words = pd.read_csv(self.etymologies_csv_file)
        except:
            raise Exception("Error: cannot update master csv without an etymologies file: "+self.etymologies_csv_file)
        
        master_words = pd.read_csv(self.master_csv_file)

        words.fillna('',inplace=True)
        master_words.fillna('',inplace=True)

        for rr,word_row in words.iterrows():
            this_word = word_row['word']
            if this_word not in master_words['word'].values:
                if word_row['root language']<>'':
                    d = {}
                    for key in etymology_keys:
                        d[key] = words.loc[rr,key]
                    master_words.append([d])

        master_words.to_csv(self.master_csv_file,na_rep="",index=False)
    

    def get_root_word(self,the_word):

        print ""
        print "Trying to look for roots of %s"%(the_word)


        # pick out synonyms from the synset that are basically the same word (share first 3 letters)
        # (and also strip them of part of speech,
        #  n., v., and so on...)
        #
        # synsets look like:
        # swing.n.04
        # 
        # so use .split('.')[0] (first token before .)
        #
        try:
            full_synset = Word(the_word).synsets
            full_synset_strings = [syn.name().split('.')[0] for syn in full_synset]
        except:
            full_synset_strings = []

        # only keep the suggested synset 
        # if the first three letters of the synset
        # match the first three letters of the original word
        # (synset returns lots of diff words...)
        synset = []
        for sss in zip(full_synset_strings):
            if sss[:3] == the_word[:3]:
                synset.append(sss)


        # first try removing any common suffixes

        # -ed
        if the_word[-2:]=='ed':
            # -ed to -
            # consonant, more likely, so prepend
            synset.insert(0,the_word[:-2])

            # -ed to -e
            synset.append(the_word[:-1])

        # -ing
        if the_word[-3:]=='ing':
            # -ing to -
            synset.insert(0,the_word[:-3])

        # -ly
        if the_word[-2:]=='ly':
            # -ly to -
            synset.insert(0,the_word[:-2])

        # -es
        if the_word[-2:]=='es':
            # -es to -
            synset.insert(0,the_word[:-2])
            # -es to -e
            synset.append(the_word[:-1])



        return synset




    def etymonline_lookup(self,the_word):
        """
        Returns a BeautifulSoup object
        containing the results of the search
        """

        browser = mechanize.Browser()
        response = browser.open('http://www.etymonline.com/')
        browser.select_form(nr=0)
        try:
            browser['search'] = the_word
        except TypeError:        
            pass
        resp = browser.submit()
        html_doc = resp.read()
        soup = BeautifulSoup(html_doc)

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

            print "Loading existing words CSV..."
            words = pd.read_csv(self.words_csv_file)
            assert('word' in words.columns)
            print "done"

        elif os.path.isfile(self.etymologies_csv_file):

            print "Loading existing etymologies CSV..."
            words = pd.read_csv(self.etymologies_csv_file)
            assert('word' in words.columns)
            print "done"


        else:

            print "Opening HTML..."
            with open(self.html_file,'r') as f:
                html_doc = f.read()
            soup = BeautifulSoup(html_doc)
            print "done"



            # ------
            # page text
            # <p>
            # the texttags contain the text
            print "Turning HTML into text..."
            texttags_all = [tt for tt in soup.findAll('p',text=True)]
            texttags = []
            for tta in texttags_all:
                if 'class' in tt.attrs.keys():
                    if tt.attrs['class']=='toc':
                        pass
                texttags.append(tta)
            print "len(texttags) =",len(texttags)

            all_text = []
            for tt in texttags:
                all_text.append(tt.string)

            if self.do_definitions:
                if len(word)>2:
                    deff = Word(word).definitions
                    if deff <> []:
                        definition = "; ".join(deff)
                        d['definition'] = definition 

            s = " ".join(all_text)
            s = unicode(s)

            t = TextBlob(s)
            print "done"

            print "Getting word counts..."
            wc = t.word_counts
            print "done"
        
            words = pd.DataFrame([])

            print "Populating words..."
            for the_word in wc.keys():
                the_word = the_word.lower()
                d = {}
                d['word'] = the_word.encode('utf-8')
                d['word count'] = wc[the_word]

                ## make space in the dataframe for later analysis
                #d['root language']=''
                #d['second language']=''
                #d['ranked languages']=''

                if self.do_definitions:
                    if len(word)>2:
                        deff = Word(word).definitions
                        if deff <> []:
                            definition = "; ".join(deff)
                            d['definition'] = definition 

                words = words.append([d])

            print "done"
            
            print "Reindex according to word count ranking..."
            words = words.sort(columns=['word count','word'],ascending=[False,True])
            words.index = range(1,len(words)+1)
            print "done"


            print "Exporting to file..."
            words.to_csv(self.words_csv_file,index=False,na_rep="")
            print "done"



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
        print "Loading words CSV..."
        try:
            words = pd.read_csv(self.words_csv_file)
        except:
            raise Exception("Error: need a words CSV file to proceed: "+self.words_csv_file)
        words.fillna('',inplace=True)
        print "done"

        wordlist = list(words['word'].values)


        etymology_keys = ['root word','root language','second language','ranked languages']
        for key in etymology_keys:
            if key not in words.columns:
                words[key] = ''


        # check if master word list exists
        #if os.path.isfile(self.master_csv_file):

        # or just force make one
        if False:

            print "Populating etymology information from previous master list..."

            # populate any missing word etymology entries 
            # from the master word list:
            master_words = pd.read_csv(self.master_csv_file)
            master_words.fillna('',inplace=True)

            shared_wordlist = list(master_words['word'])

            for rr,word_row in words.iterrows():
                this_word = word_row['word']
                if this_word in master_words['word'].values:
                    # we need to do .values[0]
                    for key in etymology_keys:
                        words.loc[rr,key] = master_words.loc[master_words['word']==this_word,key].values[0]
                        #try:
                        #except:
                        #    import pdb; pdb.set_trace()
                        #    a=0
        else:
            master_words = pd.DataFrame([])

        init_print = False
        try:
            untagged = len([j for j in words['root language'].values if j<>''])
        except KeyError:
            untagged = []
        print "Beginning etymology lookups with 0 of",len(wordlist),"words, ",untagged,"untagged words"

        for cc,word_row in words.iterrows():

            the_word = word_row['word']

            # if a word is done, don't bother looking it up.
            if 'root language' in word_row.keys():
                if word_row['root language']<>'':
                    continue

            if len(the_word)<2:
                continue


            # First, look for the word itself.
            # If that doesn't work, try variations.

            found_result = False

            # ------------
            # Original word

            # now use beautifulsoup to go through resp.read()
            soup = self.etymonline_lookup(the_word)
    
            matching_words = {}
            root_words = {}
        
            # dt = dictionary term
            dts = soup.find_all('dt')
        
            # dd = dictionary definition
            dds = soup.find_all('dd')
    
            # Look for original word 
            # in each search result
            # (searching for original word)
            for dt,dd in zip(dts,dds):
    
                # get the text of the term
                # in the form:
                # this (n.)
                # that (n.)
                # foo (v.)
                # bar (adj.)
                this_word_full = dt.get_text()
    
                # remove (n./adj./v.) 
                # ("the" is the only word that doesn't have n/adj/v)
                if the_word<>'the':
                    #this_word = this_word_full.split(' ')[:-2]
                    this_word = this_word_full.split(' ')[0]
                    this_word = ''.join(this_word)
                else:
                    this_word = this_word_full
                this_word = this_word.strip()


                if the_word.lower()==this_word.lower():
                    # We have an exact match!
    
                    # key is the_word 
                    # or 
                    # key is this_word
    
                    # get etymology from the dd tag
                    # corresponding to our dt tag
                    etym = dd.get_text()
    
                    # etymology is the value
                    matching_words[the_word] = etym
                    root_words[the_word] = the_word
    
                    # yay!
                    found_result = True
    
                    break
    
    
            # Now check for common suffixes...
            if found_result == False:

                roots = self.get_root_word(the_word)

                # look for each root
                for root in roots:

                    soup = self.etymonline_lookup(root)

                    for dt,dd in zip(dts,dds):
    
                        # get the text of the term
                        this_word_full = dt.get_text()
    
                        # remove (n./adj./v.) 
                        this_word = this_word_full.split(' ')[:-2]
                        this_word = ''.join(this_word)
    
                        if the_word.lower() == root.lower():
                            # We have an exact match!
    
                            # key is the_word 
                            # or 
                            # key is this_word
    
                            # get etymology from the dd tag
                            # corresponding to our dt tag
                            etym = dd.get_text()
    
                            # etymology is the value
                            matching_words[the_word] = etym
                            root_words[the_word] = root
    
                            # yay!
                            found_result = True
    
                            break
    
    
            # if found_result is False,
            #    FAIL...!!! 
            #    we are skipping this word
            # 
            # 
            # but otherwise...
            #     we extract etymology info!
            if found_result:
    
                # remember:
                # the_word is lowercase
                # just to avoid confusion.
    
                # 
                # avoid false positives...
                if the_word in matching_words.keys():
    
                    etymology = matching_words[the_word]

                    root_word = root_words[the_word]
    
                    # create a grid with location (in etymology) of each language's reference.
                    ## old way (incorrect, 'Germanic' always flags 'German' too)
                    #etymology_grid = [etymology.index(lang) if lang in etymology else -1 for lang in languages]
                    etymology_grid = []
    
                    for lang in languages:
    
                        # need to do re
                        # need to compile these in a list
    
                        m = re.search(lang+r'\b', etymology)
    
                        # double check if N is actually Old N
                        n = re.search('Old '+lang+r'\b', etymology)
    
                        if (m and not n):
                            etymology_grid.append( m.start() )
                        else:
                            etymology_grid.append(-1)
    
                    # each word is tagged with whatever language 
                    # is referenced FIRST in the etymology
    
                    # get whole grid
                    etymology_grid_gt0 = [eg for eg in etymology_grid if eg >= 0 ]
    
                    # check whether there IS a result
                    if len(etymology_grid_gt0)>0:
    
                        # etymology_grid_gt0 contains the ranked order of each language. min means it comes first.
                        #
                        # (Pdb) p etymology_grid
                        # [-1, 239, 227, -1, 188, 184, 71, 71, 138, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1]
                        #
                        # (Pdb) etymology_grid_gt0
                        # [239, 227, 188, 184, 71, 71, 138, 0]
                        #
                        # (Pdb) p [languages[ii] for ii in range(len(etymology_grid)) if etymology_grid[ii] > 0]
                        # ['Greek', 'Latin', 'Norse', 'Old Norse', 'German', 'Dutch']
                        #
                        sorted_etymology_grid = sorted(etymology_grid_gt0)
    
                        ranking = []
                        for ii,et in enumerate(etymology_grid):
    
                            if et>=0:
                                val = sorted_etymology_grid.index(et)
                            else:
                                val = -1
    
                            ranking.append(val)
    
                        ranked_langs = [languages[r] for r in ranking if r > -1] 
                        ranked_languages = ";".join(ranked_langs)
    
                        try:
                            language1_name = ranked_langs[0]
                        except:
                            language1_name = ''
    
                        try:
                            language2_name = ranked_langs[1]
                        except:
                            language2_name = ''

                        ranked_languages = ";".join(ranked_langs)
        
                        print ""
                        print "Tagging word %d of %d: %s"%(cc,len(wordlist),the_word)
    
                        print the_word,":",language1_name
    
                        etymology_info = [root_word,language1_name,language2_name,ranked_languages]
                        d = {}
                        for key,info in zip(etymology_keys,etymology_info):
                            d[key] = info
                            words.loc[cc,key] = info 
                        master_words.append([d])
                        words.append([d])

            else:
                # no result found. mark it '' and not NaN.
                for key in etymology_keys:
                    words.loc[cc,key]=''

            if cc%50==0:
                print "Exporting to file..."
                words.to_csv(self.etymologies_csv_file,na_rep="",index=False)
                print "done"
    
        print "Exporting to file..."
        words.to_csv(self.etymologies_csv_file,na_rep="",index=False)

        # also export the new words we've added to master
        master_words.to_csv(self.master_csv_file,na_rep="",index=False)
        print "done"






