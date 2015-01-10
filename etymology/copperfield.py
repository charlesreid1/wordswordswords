from textblob import TextBlob, Word
import mechanize
from bs4 import BeautifulSoup
import pandas as pd
import re
import logging
import time


logging.basicConfig(filename='copperfield.log',level=logging.DEBUG)

text = '../data/copperfield_ch1.txt'
copperfield_html_file = 'gutenberg/copperfield.html'
#copperfield_html_url = 'http://www.gutenberg.org/files/766/766-h/766-h.htm'

# whole thing
csvfile = 'csv_copperfield_words.csv'
htmlfile = 'copperfield_body.html'

from languages import languages, languages_key

def main():
    # First, we want to export definition and language to a file.
    # But this takes a long time, and we only want to do it once.

    t0 = time.time()

    export_file(csvfile)

    t1 = time.time()

    # Next, we want to read the text, tag it, export to html
    s = gen_html_file(csvfile,htmlfile)

    t2 = time.time()

    msg = 'Exporting word/etymology file took %0.1f s'%(t1-t0)
    msg2 = 'Creating HTML file took %0.1f s'%(t2-t1)
    logging.info(msg)

    print msg 
    print msg2



def gen_html_file(csvfile,htmlfile):

    words = pd.read_csv(csvfile)
    words = words.fillna("")

    words_w_lang = words[words['root language']<>'']

    print "Tagging HTML..."
    print "Be patient! Tagging",len(words_w_lang),"words..."

    # BeautifulSoup to load html
    # find h1 (book title) title
    # iterate chapter by chapter

    ## read live,
    ## and get kicked off of gutenberg
    ## b/c they think you're a bot
    ## (which you are)
    #browser = mechanize.Browser()
    #response = browser.open(copperfield_html_url)
    #html_doc = response.read()

    # save file locally
    with open(copperfield_html_file,'r') as f:
        html_doc = f.read()

    soup = BeautifulSoup(html_doc)



    # ------
    # title and author
    titletag = soup.findAll('h1',text=True)[0]
    title = titletag.string

    authortag = soup.findAll('h2',text=True)[0]
    author = re.sub('By ','',authortag.string)




    # -----
    # table of contents
    tocs = [toc for toc in soup.findAll('p',{"class":"toc"})]




    # ------
    # page text
    # <p>
    # or chapter markers
    # <h2>
    # the booktags contain the book text
    booktags = [tt for tt in soup.findAll(['p','h2'],text=True)]
    print "len(booktags) =",len(booktags)

    # ~7k paragraphs in the novel

    # this is a list of Tag objects
    # that will be passed to BeautifulSoup
    # at the very end and turned into a 
    # final page...
    new_body = []

    iptot = len(booktags)
    ip = 1
    ich = 1
    for booktag in booktags:


        if booktag.name=='h2':

            # skip this one - it is the author
            if ich==1:
                ich += 1
                pass

            # chapter heading
            if True:
                print "Tagging chapter heading",ich

            #if ich==7:
            #    break

            ich += 1

            new_body.append( unicode(booktag) )




        elif booktag.name=='p':

            if ip%5==0:
                print "Tagging paragraph",ip,"of",iptot

            #if ip%50==0 or ip==1:
            #    print "Tagging paragraph",ip,"of",10#iptot
            #if ip==10:
            #    break

            ip += 1

            # process paragraph text:
            # loop through each word in our etymology dataframe,
            # and tag each word that we find in it.

            #
            # split is the variable we'll be modifying on the fly.
            # we'll go through split word-by-word and see if it is 
            # in our etymology dataframe.
            # if it is, we'll change that item in split to be 
            # the word plus the tag. e.g.,
            # 
            # split = [ ... , 'python', ... ]
            # 
            # becomes
            # 
            # split = [ ... , '<div class="latin">python</div>', ... ]
            # 
            # this is all re-joined at the end with a ' '.join(split)
            #

            split = booktag.string.split()

            if booktag.string <> None:

                iw = 1
                for _,word_row in words_w_lang.iterrows():

                    #if (ip%50==0 or ip==1) and (iw%500==0 or iw==1):
                    #    print "    Tagging word",iw,"of",len(words_w_lang)
                    iw += 1 

                    word = word_row['word']
                    full_lang = word_row['root language']
                    lang = languages_key[full_lang]

                    for it,token in enumerate(split):
                        if token.lower() == word.lower():
                            split[it] = '<span class="' + lang + '">' + token + '</span>'

                new_ptag_html = ' '.join(split)

                new_body.append( "<p>" + new_ptag_html + "</p>" )


    print "done"

    print "Making some soup"
    soup = BeautifulSoup(' '.join(new_body))
    print "done"

    print "\n","*"*20,"\n"

    print "Writing to file",htmlfile
    to_html(htmlfile,soup)
    print "done"



def to_html(htmlfile,soup):
    with open(htmlfile,'w') as f:
        f.write(soup.prettify().encode('utf-8'))



def open_text(text_file):
    """
    text_file : location of text to open

    returns textblob
    """

    print "Opening text..."
    with open(text_file) as f:
        s = f.read()
    s = s.decode('utf-8')
    print "Done."

    print "Making textblob..."
    t = TextBlob(s)
    print "done"

    return t



def export_file(csvfile):
    export_word_file(csvfile,do_definitions=False)
    export_language_file(csvfile)




def export_word_file(csvfile_def,do_definitions):
    """
    Creates Pandas dataframe with words
    (and optionally, definitions)

    Exports to csv file
    """

    t = open_text(text)

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

