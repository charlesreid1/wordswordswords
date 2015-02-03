from textblob import TextBlob, Word
import mechanize
from bs4 import BeautifulSoup
import pandas as pd
import re
import logging
import time
import os.path
from languages import languages, languages_key



class EtymologyHTML(object):
    """
    Step 2: Etymology CSV -> Etymology HTML

    This class is for turning a CSV with etymology information
    into an HTML with tagged words.
    """

    def __init__(self,name_):
        """
        Quick set up of etymology csv object.
        """
        self.gutenberg_file = "gutenberg/"+name_+".html"
        self.csv_file  = "csv/"+name_+"_etymologies.csv"
        self.html_file = "html/"+name_+".html"
        self.log_file  = "log/"+name_+".log"
        self.temp_file = "html/temp_"+name_+".html"
        self.name_ = name_



    def export_html_file(self):
        """
        First check if we have an HTML file underway.

        If so, add it to our list of strings, 
        find our starting place, and keep going.

        If not, load the etymology data container.
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


        
        # new body contains the list of 
        # strings that will form our new 
        # html file.
        new_body = []



        # Check if we already have html file
        # (export finished or underway)

        if os.path.isfile(self.html_file):

            # Yes, we have an existing html file
            # (finished or underway) 
            with open(self.html_file,'r') as f:
                html_doc2 = f.read()
            soup2 = BeautifulSoup(html_doc2)
            
            # now that we have both html docs
            # as soups... compare last <p>
            if soup.p[-1].lower()==soup2.p[-1].string.lower():
                # We are finished
                print "Found a finished HTML file in",self.html_file

            else:
                # We are not finished
                print "Found an unfinished HTML file in",self.html_file

                # populate new_body
                # with soup2

                # Check if last paragraph is in gutenberg
                # If so, pick up at that <p> index
                gutenberg_ps = soup.findAll('p',text=True)
                gutenberg_text = [p.string.lower() for p in gutenberg_ps]

                if soup2.p[-1].string.lower() in gutenberg_text:
                    print "Picking up where we left off..."
                else:
                    raise Exception("I'm lost!")




        else:

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





            # prepend some front-matter tags 
            # this info will be used by Pelican 
            new_body = ["<html><head><title>"+title+"</title>",
                        "<meta name=\"author\" content=\"" + self.author + "\" />",
                        "<meta name=\"save_as\" content=\"" + self.name_ + ".html\" />",
                        "</head><body>" ]



            # -----
            # table of contents
            tocs = [toc for toc in soup.findAll('p',{"class":"toc"})]


            # ------
            # page text
            # <p>
            # or chapter markers
            # <h2>
            # the booktags contain the book text
            booktags = [tt for tt in soup.findAll(['p','h2'],text=True)]
            print "len(booktags) =",len(booktags)

            # ~7k paragraphs in the novel

            # this is a list of Tag objects
            # that will be passed to BeautifulSoup
            # at the very end and turned into a 
            # final page...
            new_body = []

            iptot = len(booktags)
            ip = 1
            ich = 1
            for booktag in booktags:


                if booktag.name=='h2':

                    # skip first and second ones - both are author
                    if ich==1 or ich==2:
                        ich += 1
                        pass

                    # chapter heading
                    if True:
                        print "Tagging chapter heading",ich

                    # dump everything we have so far, first
                    if ich%2==0:
                        print "Making some backup soup"
                        soup = BeautifulSoup(' '.join(new_body))
                        with open(self.html_file,'w') as f:
                            f.write(soup.prettify().encode('utf-8'))
                        print "done"


                    ich += 1

                    new_body.append( unicode(booktag) )



                    # this should be a whole separate file




                elif booktag.name=='p':

                    if ip%5==0:
                        print "Tagging paragraph",ip,"of",iptot

                    #if ip%50==0 or ip==1:
                    #    print "Tagging paragraph",ip,"of",10#iptot
                    #if ip==10:
                    #    break

                    ip += 1

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

                    split = booktag.string.split()

                    if booktag.string <> None:

                        iw = 1
                        for _,word_row in words_w_lang.iterrows():

                            #if (ip%50==0 or ip==1) and (iw%500==0 or iw==1):
                            #    print "    Tagging word",iw,"of",len(words_w_lang)
                            iw += 1 

                            word = word_row['word']
                            full_lang = word_row['root language']
                            lang = languages_key[full_lang]

                            for it,token in enumerate(split):
                                if token.lower() == word.lower():
                                    split[it] = '<span class="' + lang + '">' + token + '</span>'

                        new_ptag_html = ' '.join(split)

                        new_body.append( "<p>" + new_ptag_html + "</p>" )

            # finish up the tags
            new_body.append("</body></html>")

            print "done"

            print "Making some soup"
            soup = BeautifulSoup(' '.join(new_body))
            print "done"


        print "\n","*"*20,"\n"

        print "Writing to file",self.html_file
        with open(self.html_file,'w') as f:
            f.write(soup.prettify().encode('utf-8'))
        print "done"


