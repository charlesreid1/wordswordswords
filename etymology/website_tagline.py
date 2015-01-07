from textblob import TextBlob, Word
import mechanize
from bs4 import BeautifulSoup
import pandas as pd

text = '../data/small.txt'

csvfile = 'csv_small.csv'
htmlfile = 'small_body.html'

languages = ['French','Greek','Latin', \
             'Sanskrit','Norse','Old Norse','German','Germanic', \
             'Dutch','Welsh','Irish','Old English','Russian', \
             'Slavonic','American English','Arabic','Spanish','Polish','Turkish']

languages_key = {}
languages_key['French']             ='french'
languages_key['Greek']              ='greek'
languages_key['Latin']              ='latin'
languages_key['Sanskrit']           ='sanskrit'
languages_key['Norse']              ='norse'
languages_key['Old Norse']          ='oldnorse'
languages_key['German']             ='german'
languages_key['Germanic']           ='germanic'
languages_key['Dutch']              ='dutch'
languages_key['Welsh']              ='welsh'
languages_key['Irish']              ='irish'
languages_key['Old English']        ='oldenglish'
languages_key['Russian']            ='russian'
languages_key['Slavonic']           ='slavonic'
languages_key['American English']   ='americanenglish'
languages_key['Arabic']             ='arabic'
languages_key['Spanish']            ='spanish'
languages_key['Polish']             ='polish'
languages_key['Turkish']            ='turkish'

def main():
    # First, we want to export definition and language to a file.
    # This is expensive, if text is long. 
    # Looks up each word on Online Etymology Dictionary.
    export_file(csvfile)

    # Next, we want to read the text, tag it, export to html
    s = gen_html_file(csvfile,htmlfile)




def gen_html_file(csvfile,htmlfile):

    words = pd.read_csv(csvfile)
    words = words.fillna("")

    t = open_text(text)

    words_w_lang = words[words['root language']<>'']

    print "Obtaining tokens..."
    tokens = t.tokenize()._collection
    print "done"

    print "Modifying tokens..."
    ii=0
    for _,word_row in words_w_lang.iterrows():

        if ii%100==0:
            print "Tagging word",ii,"of",len(words_w_lang),"(",word_row['word'],")"

        word = word_row['word'].encode('utf-8')
        lang = word_row['root language']

        print "  Modifying token",word
        for zz,tok in enumerate(tokens):
            if tok.lower()==word.lower():
                tokens[zz] = '<span class="'+languages_key[lang]+'">'+tok+'</span>'

        ii += 1

    print "done"

    print "Cleaning up..."
    for zz,tok in enumerate(tokens):
        if 'chapter' in tok:
            tokens[zz] = '</p><p>' + tokens[zz]
    print "done"

    fulltext = ' '.join(tokens)

    to_html(htmlfile,fulltext)




def to_html(htmlfile,s):
    with open(htmlfile,'w') as f:
        f.write("<p>")
        f.write(s.encode('utf-8'))
        f.write("</p>")



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
    export_definition_file(csvfile)
    export_language_file(csvfile)


def export_definition_file(csvfile_def):
    """
    Creates Pandas dataframe with definitions
    Exports to csv file
    """

    t = open_text(text)

    print "Getting word counts..."
    wc = t.word_counts
    print "done"
    
    words = pd.DataFrame([])

    print "Populating words..."
    for the_word in wc.keys():
        d = {}
        d['word'] = the_word.encode('utf-8')
        d['word count'] = wc[the_word]
        words = words.append([d])
    print "done"
    
    print "Reindex according to word count ranking..."
    words = words.sort(columns=['word count','word'],ascending=[False,True])
    words.index = range(1,len(words)+1)
    print "done"
    
    #print "Getting definitions of words..."
    #words['definition']=''
    #for word in words['word'].values:
    #    if len(word)>2:
    #        deff = Word(word).definitions
    #        if deff <> []:
    #            definition = "; ".join(deff)
    #            words['definition'][words['word']==word] = definition
    #print "done"

    words['root language']=''

    print "Exporting to file..."
    words.to_csv(csvfile_def,na_rep='')
    print "done"



def export_language_file(csvfile_lang):

    words = pd.read_csv(csvfile_lang)
    wordlist = list(words['word'].values)

    for cc,the_word in enumerate(wordlist):

        the_word = the_word.lower()
    
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
    
        for dt,dd in zip(dts,dds):
            this_word_full = dt.get_text()
    
            # remove (n./adj./v.) 
            this_word = this_word_full.split(' ')[:-2]
            this_word = ''.join(this_word)
            
            if the_word in this_word:
                # word is the key
                etym = dd.get_text()
                # etymology is the value
                matching_words[this_word] = etym

            elif the_word[0:2]==this_word[0:2]:
                etym = dd.get_text()
                matching_words[this_word] = etym

    
        if the_word in matching_words.keys():
            # match!
            etymology = matching_words[the_word]
            # create a grid with location (in etymology) of each language's reference.
            etymology_grid = [etymology.index(lang) if lang in etymology else -1 for lang in languages]
            # now we should have a way to determine the order of each language reference
            # and therefore a way of prioritizing which languages are tagged for a given word.
            ###print the_word,":",etymology_grid
    
            # each word is tagged with whatever language 
            # is referenced FIRST in the etymology
            etymology_grid_gt0 = [eg for eg in etymology_grid if eg >= 0 ]
    
            # check whether there IS a result
            if len(etymology_grid_gt0)>0:

                # etymology_grid_gt0 contains the ranked order of each language. min means it comes first.
                first_lang_ref = min(etymology_grid_gt0)
                last_lang_ref = max(etymology_grid_gt0)
    
                # what language are we using? (index)
                the_language_index = etymology_grid.index(first_lang_ref)
    
                # what language are we using? (language name)
                the_language_name = languages[the_language_index]
    
                print ""
                print "Tagging word %d of %d: %s"%(cc,len(wordlist),the_word)
    
                print the_word,":",the_language_name

                words['root language'][words['word']==the_word] = the_language_name

        if cc%50==0:
            print "Exporting to file..."
            words.to_csv(csvfile_lang,na_rep="")
            print "done"

    print "Exporting to file..."
    words.to_csv(csvfile_lang,na_rep="")
    print "done"


if __name__=="__main__":
    main()


