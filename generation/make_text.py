from __future__ import division
import re
import codecs
import nltk
from nltk.tokenize import WordPunctTokenizer 
from ngram import *

filenames = ['crimeandpunishment.txt',
             'brotherskaramazov.txt',
             'theidiot.txt']

for ii,filename in enumerate(filenames):

    with codecs.open('../data/'+filename,encoding='utf-8') as f:

        print "======================================"
        print filename 
        print "======================================"

        bk = f.read()
        bk = bk.replace('\r\n',' ')

        tok = WordPunctTokenizer().tokenize(bk)

        import pdb; pdb.set_trace()
        content = content_model.generate(starting_words)


