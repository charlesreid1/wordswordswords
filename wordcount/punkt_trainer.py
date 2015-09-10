from __future__ import division
import re
import nltk
from nltk.tokenize import WordPunctTokenizer 
from nltk.text import Text
import matplotlib.pylab as plt
import numpy as np
from scipy import stats
import brewer2mpl
import codecs

filenames = ['crimeandpunishment.txt',
             'brotherskaramazov.txt',
             'theidiot.txt']



fig = plt.figure(figsize=(6,8))
ax = fig.add_subplot(111)

bmap = brewer2mpl.get_map('Dark2','qualitative',len(filenames))
colors = bmap.mpl_colors

for ii,filename in enumerate(filenames):

    with codecs.open('../data/'+filename,encoding='utf-8') as f:

        print "======================================"
        print filename 
        print "======================================"

        bk = f.read()
        bk = bk.replace('\r\n',' ')

        tok = WordPunctTokenizer().tokenize(bk)

        num_wds = len(tok)
        print "Number of words, "+filename+":",num_wds

        num_uniq_wds = len(set(tok))
        print "Number of unique words, "+filename+":",num_uniq_wds

        richness = num_uniq_wds/num_wds
        print "Lexical Richness (# uniq words/# words) %s: %0.4f"%(filename,richness)

        print "\n"+"-"*40+"\n\n"

        z = [len(j) for j in tok]

        kernel = stats.gaussian_kde(z,'scott')
        xx = np.linspace(1,max(z),max(z))

        ax.plot(xx,kernel(xx),'o-',color=colors[ii],label=filename)
        ax.grid()
        ax.set_xlim([0,20])
        ax.set_xlabel('Word Length')
        ax.set_ylabel('P(WL)')

        print "\n"*2

ax.legend(loc='best')
fig.savefig('../img/kde_wordlength.png')
plt.show()
plt.draw()


