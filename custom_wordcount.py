from __future__ import division
import re
import nltk
from nltk.tokenize.punkt import PunktWordTokenizer
from nltk.text import Text
import matplotlib.pylab as plt

dostoyevsky_filenames=['crimeandpunishment.txt',
                       'brotherskaramazov.txt',
                       'theidiot.txt']

filenames=['nyker_graphene.txt']

for filename in filenames:

    with open('data/'+filename) as f:

        print "======================================"
        print filename 
        print "======================================"

        bk = f.read()
        bk = bk.replace('\r',' ')
        bk = bk.replace('\n',' ')

        tok = PunktWordTokenizer().tokenize(bk)

        ln = len(tok)
        print "Length of "+filename+":",ln

        nw = len(set(tok))
        print "Num Words "+filename+":",nw

        richness = nw/ln
        print "Lexical Richness %s: %0.4f"%(filename,richness)

        print "\n"+"-"*40+"\n\n"

        fdist = nltk.FreqDist(tok)
        mc = fdist.most_common(10)
        for ww in mc:
            print "%s\t\t%d"%(ww)#word,wordfreq)

        ### fdist.plot(50, cumulative=True)

        z = [len(j) for j in tok]
        fig = plt.figure()
        ax1 = fig.add_subplot(111)

        ax1.hist(z,40,color='g',bottom=0.001)

        ax1.set_title(filename)
        ax1.set_yscale('log')

        figname = filename[:-4]+'.jpg'
        print figname

        plt.show()
        plt.draw()
        fig.savefig('img/'+figname)

        print "\n"*2
