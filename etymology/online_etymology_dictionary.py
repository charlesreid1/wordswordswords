import mechanize
from bs4 import BeautifulSoup
from nltk.tokenize.punkt import PunktWordTokenizer
import nltk


languages = ['French','Greek','Latin', \
             'Sanskrit','Norse','Old Norse','German','Germanic', \
             'Dutch','Welsh','Irish','Old English','Russian', \
             'Slavonic','American English','Arabic','Spanish','Polish','Turkish']

pl = """
Of Man's first disobedience, and the fruit
Of that forbidden tree whose mortal taste
Brought death into the World, and all our woe,
With loss of Eden, till one greater Man
Restore us, and regain the blissful seat,
Sing, Heavenly Muse, that, on the secret top
Of Oreb, or of Sinai, didst inspire
That shepherd who first taught the chosen seed
In the beginning how the heavens and earth
Rose out of Chaos: or, if Sion hill
Delight thee more, and Siloa's brook that flowed
Fast by the oracle of God, I thence
"""

tok = PunktWordTokenizer().tokenize(pl)
tok2 = set(tok)

for the_word in tok2:
 
    browser = mechanize.Browser()
    response = browser.open('http://www.etymonline.com/')
    browser.select_form(nr=0)
    browser['search'] = the_word
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
            first_lang_ref = min(etymology_grid_gt0)

            # what language are we using? (index)
            the_language_index = etymology_grid.index(first_lang_ref)

            # what language are we using? (language name)
            the_language_name = languages[the_language_index]

            print the_word,":",the_language_name




