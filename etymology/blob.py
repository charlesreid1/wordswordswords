from textblob import TextBlob, Word
import mechanize
from bs4 import BeautifulSoup

n0 = 500
n = 550


languages = ['French','Greek','Latin', \
             'Sanskrit','Norse','Old Norse','German','Germanic', \
             'Dutch','Welsh','Irish','Old English','Russian', \
             'Slavonic','American English','Arabic','Spanish','Polish','Turkish']

print "Opening copperfield..."
#with open("test.txt") as f:
with open("../data/copperfield.txt") as f:
    s = f.read()
s = s.decode('utf-8')
print "Done."

print "Making textblob..."
t = TextBlob(s)
print "done"

print "Getting word counts..."
wc = t.word_counts
print "done"

keys = wc.keys()
vals = wc.values()

trimmed_keys = []
trimmed_vals = []
print "Trimming word counts..."
for k,v in zip(keys,vals):
    if k!=0 and len(k)>2:
        trimmed_keys.append(k)
        trimmed_vals.append(v)
print "done"

print "Sorting word counts..."
from operator import itemgetter
vals_sorted, keys_sorted = zip(*sorted(zip(trimmed_vals,trimmed_keys),
    key=itemgetter(0),reverse=True))
print "done"

#print "Trimming word counts..."
#wc = [w for w in t.word_counts if len(w[0]) > 2]
#print "done"

wordlist = [j for j in keys_sorted[n0:n]]

print "-"*40
print wordlist
print "-"*40

for cc,the_word in enumerate(wordlist):

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

            print ""
            print "Word %d of %d: %s"%(n0+cc,n0+len(wordlist),the_word)

            print the_word,":",the_language_name


#print t.words
#print t.word_counts['the']

#bb = t.sentences[4]
#print bb
#print bb.translate(to='es')
#print bb.translate(to='ar')
#print bb.translate(to='fr')
#print bb.translate(to='zh-cn')

#print Word('octopus').definitions

#print t.word_counts


