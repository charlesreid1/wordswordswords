from __future__ import division
import nltk
from nltk.tokenize.punkt import PunktWordTokenizer
from nltk.text import Text

filenames=['data/crimeandpunishment.txt',
           'data/brotherskaramazov.txt',
           'data/theidiot.txt']

for filename in filenames:

    with open(filename) as f:

        print "======================================"
        print filename 
        print "======================================"

        bk = f.read()
        bk = bk.replace('\r','')
        bk = bk.replace('\n','')

        tok = PunktWordTokenizer().tokenize(bk)

        ln = len(tok)
        print "Length of "+filename+":",ln

        nw = len(set(tok))
        print "Num Words "+filename+":",nw

        richness = nw/ln
        print "Lexical Richness %s: %0.3e"%(filename,richness)

        print "\n"+"-"*40+"\n\n"

        fdist = nltk.FreqDist(tok)
        mc = fdist.most_common(100)
        for ww in mc:
            print "%s\t\t%d"%(ww)#word,wordfreq)

        fdist.plot(50, cumulative=True)

        #import pdb; pdb.set_trace()
        #a=0

        print "\n"*2
