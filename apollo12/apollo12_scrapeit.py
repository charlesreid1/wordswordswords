import mechanize 
from bs4 import BeautifulSoup
from util import *
import nltk
import re

"""
-------------------------------------------------------
extract transcripts from the lunar surface journals
and reformat to feed to olipy

https://www.hq.nasa.gov/alsj/main.html

apollo 12:
http://www.hq.nasa.gov/office/pao/History/ap12fj/index.htm

jan 2015
-------------------------------------------------------
"""

#####################################
# apollo 12
#
# consists of 10 days,
# 20 links total

base_link = 'http://www.hq.nasa.gov/office/pao/History/ap12fj/'

base_page = 'index.htm'

browser = mechanize.Browser()
headers=[('Content-type', 'application/x-www-form-urlencoded; charset=UTF-8')]
browser.addheaders = headers
resp = browser.open(base_link+base_page)

html_doc = resp.read()
# now use beautifulsoup to go through resp.read()

soup = BeautifulSoup(html_doc)
log_links = []

# 
a_s = soup.find_all('a')

for a_ in a_s:
    link_text = a_.get_text()
    if 'Day ' in link_text:
        page_name = a_.attrs['href']
        link_name = base_link+page_name
        log_links.append(link_name)

# -------------------

# -------------------


# -------------------
# follow those links!!!

# a list of dictionaries with "speaker" and "token" keys
all_the_dialogue = []

hh = 0
mm = 0

line()
for i,link in enumerate(log_links):

    print "*****",(i+1),"of",len(log_links),"*****"
    print link
    #res = nltk.wordpunct_tokenize(booty.decode('utf8'))

    resp = browser.open(link)

    
    html_doc = resp.read()
    # now use beautifulsoup to go through resp.read()
    
    soup = BeautifulSoup(html_doc)

    ## pages needing special treatment
    #special_pages=[14]#[13,14]#,15]#,16,17]
    #if (i+1) in special_pages:
    #    utxt = soup.text
    #    booty = utxt.encode("utf-8")#.strip()
    #else:
    #    # type unicode
    #    utxt = soup.p.text

    #    # use something more sane:
    #    # string
    #    booty = utxt.encode("utf-8")#.strip()

    utxt = soup.text
    booty = utxt.encode("utf-8")#.strip()


    
    ## Print out what unicode symbols 
    ## were returned in the BeautifulSoup text
    #import unicodedata
    #for c in utxt:
    #    if ord(c) >= 127:
    #        print('{} U+{:04x} {}'.format(c.encode('utf8'), ord(c), unicodedata.name(c)))

    # scrub these unicode symbols from the scraped text
    unicode_key = [
        (u"\u2019",'RIGHT SINGLE QUOTATION MARK','\''),
        (u"\u2013",'EN DASH','-'),
        (u"\u00bd",'VULGAR FRACTION ONE HALF',' 1/2 '),
        (u"\u201d",'RIGHT DOUBLE QUOTATION MARK','"'),
        (u"\u201c",'LEFT DOUBLE QUOTATION MARK','"'),
        (u"\u00b7",'MIDDLE DOT','.')
        ]
    for code,name,symbol in unicode_key:
        booty = booty.decode("utf-8").replace(code,symbol).encode("utf-8")

    ## --------------------
    ## tokenize by word:
    #tokens = nltk.wordpunct_tokenize(booty)

    # tokenize by sentence:
    tokens = nltk.tokenize.sent_tokenize(booty)

    # split, then flatten list
    tokens = [j.split(": ") for j in tokens]
    tokens = [item for sublist in tokens for item in sublist]

    # split, then flatten list
    tokens = [j.split(" - ") for j in tokens]
    tokens = [item for sublist in tokens for item in sublist]

    # split, then flatten list
    tokens = [j.split("\n") for j in tokens]
    tokens = [item for sublist in tokens for item in sublist]

    # replace double quotes
    tokens = [j.replace('"','') for j in tokens]

    # no mp3 audio clips
    tokens = [j for j in tokens if 'mp3 audio' not in j.lower()]
    tokens = [j for j in tokens if ' kb.' not in j.lower()]

    comm_break = 'comm break'

    # eliminate empty items
    tokens = filter(lambda a: a <> '', tokens)

    speakers = [
        'Public Affairs Office',
        'SC',
        'MS',
        'Carr',
        'Conrad',
        'Gordon',
        'Gibson',
        'Bean',
        'ARIA',
        'MS',
        'SC',
        'Weitz',
        'Lind'
        ]

    # replace timestamps 000:00:00
    # look for "last updated" location
    #
    last_updated_index = 0
    for jj,tok in enumerate(tokens):

        if any([speaker in tok for speaker in speakers]):

            stripped_tok = re.sub('[0-9]{3}:[0-9]{2}:[0-9]{2} ','',tok)
            stripped_tok2 = re.sub('at [0-9]{3}:[0-9]{2}:[0-9x]{2}','',stripped_tok)
            stripped_tok3 = re.sub(' \(onboard\)','',stripped_tok2)
            tokens[jj] = stripped_tok3
        
        if 'last updated' in tok.lower():
            last_updated_index = jj
    
    if last_updated_index <> 0:
        tokens[0:last_updated_index+1] = []

    ii = 0
    while ii < len(tokens):
        if tokens[ii] in speakers:
            d = {}
            d['speaker'] = tokens[ii]
            ii += 1
            z = []
            while (ii<len(tokens)) and (comm_break not in tokens[ii].lower()) and (tokens[ii] not in speakers):
                z.append(tokens[ii])
                ii += 1
            d['tokens'] = z

            cc = len(all_the_dialogue)
            if ((mm+1)%60)==0:
                mm=0
            if ((cc+1)%60)==0:
                hh += 1

            d['time'] = '%03d:%02d:00'%(hh,mm)
            all_the_dialogue.append(d)
            mm += 1

        ii += 1



    # -----------------------------
    # Now that the hard part is over with...
    # we have some processing to do.
    # 
    # [Comm break.]
    # [Long comm break.]
    # [Very long comm break.]
    # 
    # Speakers:
    # Public Affairs Office
    # Carr
    # Conrad
    # Gordon
    # Gibson
    # Bean
    # ARIA
    # MS
    # SC
    # Weitz
    # Lind



    ### # output the intermediate, unparsed text
    ### filename = 'transcript'+str(i+1)+'.dat'



import json

with open('data/apollo_12.txt','w') as f:
    for d in all_the_dialogue:
        f.write(json.dumps(d))
        f.write("\n")

with open('data/apollo_12_pretty.txt','w') as f:
    json.dump(all_the_dialogue,f,indent=1)

