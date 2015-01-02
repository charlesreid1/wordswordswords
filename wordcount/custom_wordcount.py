from __future__ import division
import re
import nltk
from nltk.tokenize.punkt import PunktWordTokenizer
from nltk.text import Text
import matplotlib.pylab as plt
import numpy as np
from scipy import stats
import brewer2mpl

make_plots = False
make_freqdist = False
make_kde = True

dostoyevsky_filenames=['crimeandpunishment.txt',
                       'brotherskaramazov.txt',
                       'theidiot.txt']
other_filenames = ['nyker_graphene.txt']

poetry_filenames=['paradiselost.txt']




filenames = dostoyevsky_filenames

fig = plt.figure()
ax = fig.add_subplot(111)

bmap = brewer2mpl.get_map('Dark2','qualitative',len(filenames))
colors = bmap.mpl_colors

for ii,filename in enumerate(filenames):

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

        if make_freqdist:
            fdist = nltk.FreqDist(tok)
            mc = fdist.most_common(100)
            #for ww in mc:
            #    print "%s\t\t%d"%(ww)#word,wordfreq)

        # make kde of z
        if make_kde:

            z = [len(j) for j in tok]

            kernel = stats.gaussian_kde(z,'scott')
            xx = np.linspace(1,max(z),max(z))

            ax.plot(xx,kernel(xx),'o-',color=colors[ii],label=filename)
            ax.legend(loc='best')
            ax.grid()
            ax.set_xlim([0,20])


            #ax.hist(z,max(z),normed=True)


        if make_plots:

            fdist.plot(50, cumulative=True)

            z = [len(j) for j in tok]

            fig = plt.figure()
            ax1 = fig.add_subplot(111)

            ax1.hist(z,max(z),color='g',bottom=0.001)

            ax1.set_title(filename)
            ax1.set_yscale('log')

            figname = filename[:-4]+'.jpg'
            print figname

            fig.savefig('img/'+figname)

        print "\n"*2

plt.show()
plt.draw()

