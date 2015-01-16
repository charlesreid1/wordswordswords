from textblob import TextBlob, Word
import mechanize
from bs4 import BeautifulSoup
import pandas as pd
import re
import logging
import time
import os.path
from EtymologyHTML import *



class EtymologyChapterHTML(EtymologyHTML):
    """
    Step 2: Etymology CSV -> Etymology HTML

    This class is for turning a CSV with etymology information
    into an HTML with tagged words.
    """

    def export_html_file(self):
        """
        Load the etymology data container.
        Then loop through each paragraph, and look up 
        each word in our etymology data container.
        """
        words = pd.read_csv(self.csv_file)
        words = words.fillna("")

        words_w_lang = words[words['root language']<>'']


        # BeautifulSoup to load gutenberg
        # find h1 (book title) title
        # iterate through chapter and paragraph tags

        ## read live,
        ## and get kicked off of gutenberg
        ## b/c they think you're a bot
        ## (which you are)
        #browser = mechanize.Browser()
        #response = browser.open(copperfield_html_url)
        #html_doc = response.read()

        # save file locally
        with open(self.gutenberg_file,'r') as f:
            html_doc = f.read()

        # this is the Gutenberg text 
        # (it will be modified to make our new page)
        soup = BeautifulSoup(html_doc)



        print "Tagging HTML..."
        print "Be patient! Tagging",len(words_w_lang),"words..."


        # ------
        # title and author
        titletag = soup.findAll('h1',text=True)[0]
        title = titletag.string
        self.title = title

        authortag = soup.findAll('h2',text=True)[0]
        author = re.sub('By ','',authortag.string)
        self.author = author


        h2tags = [tt for tt in soup.findAll('h2',text=True)]
        h2tags = h2tags[2:]

        ich=1
        for h2tag in h2tags:

            print "Tagging chapter heading",ich

            h2txt = h2tag.string

            new_body = []
            
            new_body.append(unicode(h2tag))

            chapter_file = self.name_+str(ich)+".html"
            
            ptag = h2tag.findNextSibling(['p','h2'])
            if ptag == None:
                break

            ip = 0
            while ptag.name <> 'h2':

                ip += 1
                if ip%25==0:
                    print "Paragraph",ip

                # next_tag is our paragraph tag
                # and contains the text we want to extract

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

                if ptag.string<> None:

                    split = ptag.string.split()


                    for _,word_row in words_w_lang.iterrows():

                        word = word_row['word']
                        full_lang = word_row['root language']
                        lang = languages_key[full_lang]

                        for it,token in enumerate(split):
                            if token.lower() == word.lower():
                                split[it] = '<span class="' + lang + '">' + token + '</span>'

                    new_ptag_html = ' '.join(split)

                    new_body.append( new_ptag_html )


                # move on to the next tag
                ptag = ptag.findNextSibling(['p','h2'])


            print "done with chapter"

            print "Making some soup"
            soup = BeautifulSoup(' '.join(new_body))
            print "done"

            print "Writing to file",chapter_file
            with open("html/"+chapter_file,'w') as f:
                f.write(soup.prettify().encode('utf-8'))
            print "done"

            ich += 1


