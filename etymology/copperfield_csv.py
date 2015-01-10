from textblob import TextBlob, Word
import mechanize
from bs4 import BeautifulSoup
import pandas as pd
import re
import logging
import time


logging.basicConfig(filename='copperfield.log',level=logging.DEBUG)

copperfield_html_file = 'gutenberg/copperfield.html'

# whole thing
csvfile = 'csv_copperfield_words.csv'

from languages import languages, languages_key

def main():
    # First, we want to export definition and language to a file.
    # But this takes a long time, and we only want to do it once.

    t0 = time.time()

    export_word_file(csvfile,do_definitions=False)
    export_language_file(csvfile)

    t1 = time.time()

    msg = 'Exporting word/etymology file took %0.1f s'%(t1-t0)
    logging.info(msg)

    print msg 




def export_word_file(csvfile_def,do_definitions):
    """
    Creates Pandas dataframe with words
    (and optionally, definitions)

    Exports to csv file
    """


    print "Opening HTML..."
    with open(copperfield_html_file,'r') as f:
        html_doc = f.read()
    soup = BeautifulSoup(html_doc)



    # ------
    # page text
    # <p>
    # the texttags contain the text
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

    s = " ".join(all_text)
    #s = s.decode("utf-8")
    #s = s.encode("utf-8")
    #s = s.decode('ascii')
    #s = s.encode('ascii')
    s = unicode(s)

    t = TextBlob(s)

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

        d['root language']=''
        d['second language']=''
        d['ranked languages']=''

        if do_definitions:
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
    words.to_csv(csvfile_def,na_rep='',index=False)
    print "done"



def export_language_file(csvfile_lang):

    words = pd.read_csv(csvfile_lang)
    wordlist = list(words['word'].values)

    for cc,the_word in enumerate(wordlist):

        # We want to look for the root word first.
        # If we don't find anything,
        # try removing any common suffixes.

        found_result = False


        # ------------
        # Original word

        browser = mechanize.Browser()
        response = browser.open('http://www.etymonline.com/')
        browser.select_form(nr=0)
        try:
            browser['search'] = the_word
        except TypeError:        
            pass
        resp = browser.submit()
        html_doc = resp.read()
        
        # now use beautifulsoup to go through resp.read()

        soup = BeautifulSoup(html_doc)
        matching_words = {}
    
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
            this_word = this_word_full.split(' ')[:-2]
            this_word = ''.join(this_word)

            if the_word.lower()==this_word.lower():
                # We have an exact match!

                # key is the_word 
                # or 
                # key is this_word

                # get etymology from the dd tag
                # corresponding to our dt tag
                etym = dd.get_text()

                # etymology is the value
                matching_words[this_word] = etym

                # yay!
                found_result = True

                break


        # Now check for common suffixes...
        if found_result == False:

            # pick out synonyms from the synset that are basically the same word (share first 3 letters)
            # (and also strip them of part of speech,
            #  n., v., and so on...)
            #
            # synsets look like:
            # swing.n.04
            # 
            # so use .split('.')[0] (first token before .)
            #

            synset = Word(the_word).synsets
            synset_strings = [syn.name().split('.')[0] for syn in synset]

            final_synset = []
            for ss,sss in zip(synset,synset_strings):
                if sss[:3] == the_word[:3]:
                    final_synset.append(sss)

            final_synset = list(set(final_synset))

            # Look for synonyms
            # in each search result
            # (searching for each synonym)
            for dt,dd in zip(dts,dds):

                # get the text of the term
                this_word_full = dt.get_text()

                # remove (n./adj./v.) 
                this_word = this_word_full.split(' ')[:-2]
                this_word = ''.join(this_word)

                for syn in final_synset:
                    if syn.lower() == this_word.lower():
                        # We have an exact match!

                        # key is the_word 
                        # or 
                        # key is this_word

                        # get etymology from the dd tag
                        # corresponding to our dt tag
                        etym = dd.get_text()

                        # etymology is the value
                        matching_words[this_word] = etym

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
            # this_word and the_word are all lowercase...
            # just to avoid confusion.

            # 
            # avoid false positives...
            if the_word in matching_words.keys():

                etymology = matching_words[the_word]

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

                    try:
                        language1_name = ranked_langs[0]
                    except:
                        language1_name = ''

                    try:
                        language2_name = ranked_langs[1]
                    except:
                        language2_name = ''

                    #first_lang_ref = min(etymology_grid_gt0)
                    #last_lang_ref = max(etymology_grid_gt0)
    
                    print ""
                    print "Tagging word %d of %d: %s"%(cc,len(wordlist),the_word)

                    print the_word,":",language1_name

                    words.loc[words['word']==the_word,'root language'] = language1_name
                    words.loc[words['word']==the_word,'second language'] = language2_name
                    words.loc[words['word']==the_word,'ranked languages'] = ",".join(ranked_langs)

        if cc%50==0:
            print "Exporting to file..."
            words.to_csv(csvfile_lang,na_rep="")
            print "done"

    print "Exporting to file..."
    words.to_csv(csvfile_lang,na_rep="")
    print "done"







if __name__=="__main__":
    main()

