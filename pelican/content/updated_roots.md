Title: Update to Word Root Searches
Date: 2015-01-25 14:30
Category: 

In my last post, I covered the techniques I was using to deal with
failed lookups - removing suffixes and looking for root words.

My initial list of suffixes was modest:

* ```-ed```
* ```-ing```
* ```-ly```
* ```-es```
* ```-ies```

But even this got complicated, as I was checking for suffixes
preceding consonants and vowels, and still led to a lot of misses.

I expanded this, after watching the script roll through a whole
block of text and taking note of similarities in words that were
not being found in the Online Etymology Dictionary. These included words like:

* genealogical (root: genealogy)
* observing (root: observe)
* shuffling (root: shuffle)

and so on. From each cluster of words I derived the missing suffix checks 
that I needed to add to my code. The (significantly expanded) list is as follows:

* ```-ed```
* ```-ing```
* ```-ly```
* ```-es```
* ```-ies```
* ```-er```
* ```-XXed```
* ```-en```
* ```-s```
* ```-est```
* ```-ied```
* ```-ail```
* ```-ation```
* ```-ian```
* ```-ist```
* ```-sim```
* ```-ual```
* ```-iness```
* ```-liness```

Seeing this horrible nest of if/elseif/else statements gave me 
a renewed sense of appreciation for the complexity of English.
Seeing how many "special case" suffixes led to words falling through the 
cracks of the case statement, in spite of its complexity, led me to 
realize just how complicated the language mechanism in our brains can be.

To add to the complication, I had to add checks for the length of 
the word, to make sure that the word was longer than the suffix! 
(checking for a five-letter suffix on a four-letter word would 
raise exceptions...)

Here is the full suffix check as it currently stands:

    :::python

    def get_root_word(self,the_word):

        print ""
        print "Looking for roots of %s..."%(the_word)


        # pick out synonyms from the synset that are basically the same word (share first 3 letters)
        # (and also strip them of part of speech,
        #  n., v., and so on...)
        #
        # synsets look like:
        # swing.n.04
        # 
        # so use .split('.')[0] (first token before .)
        #
        try:
            full_synset = Word(the_word).synsets
            full_synset_strings = [syn.name().split('.')[0] for syn in full_synset]
        except:
            full_synset_strings = []

        # only keep the suggested synset 
        # if the first three letters of the synset
        # match the first three letters of the original word
        # (synset returns lots of diff words...)
        synset = []
        for sss in zip(full_synset_strings):
            if sss[:3] == the_word[:3]:
                synset.append(sss)


        # first try removing any common suffixes
        if len(the_word)>4:

            # -ed
            if the_word[-2:]=='ed':

                # -XXed to -X
                # wrapped to wrap, begged to beg
                if the_word[-4]==the_word[-3]:
                    synset.insert(0,the_word[:-3])

                # -ied 
                # occupied to occupy
                elif the_word[-3]=='ied':
                    synset.insert(0,the_word[-3]+"y")

                else:

                    # -ed to -
                    # consonant, more likely, so prepend
                    synset.insert(0,the_word[:-2])

                    # -ed to -e
                    # tired to tire
                    synset.append(the_word[:-1])

            # -en
            if the_word[-2:]=='en':
                # -en to -
                # quicken to quick
                synset.insert(0,the_word[:-2])

                # -en to -e
                # shaven to shave
                synset.append(the_word[:-1])

            if the_word[-2:]=='er':
                # -er to -
                # thicker to thick
                synset.insert(0,the_word[:-2])

                # -er to -e
                # shaver to shave
                synset.append(the_word[:-1])

            # -est
            if the_word[-3:]=='est':
                # -est to -
                # brightest to bright
                synset.insert(0,the_word[:-3])

                # -est to -e
                # widest to wide
                synset.append(the_word[:-2])

            # -ing
            if the_word[-3:]=='ing':
                # -ing to -
                synset.insert(0,the_word[:-3])
                # -gging to -g
                # -nning to -n
                synset.append(the_word[:-4])
                # -ing to -e
                synset.append(the_word[:-3]+"e")

            # -ly
            if the_word[-2:]=='ly':
                # -ly to -
                synset.insert(0,the_word[:-2])


        # end if len>4


        # -s/-es
        if the_word[-1:]=='s':

            # -liness
            if len(the_word)>6:
                if the_word[-6:]=='liness':
                    # -liness to -
                    # friendliness to friend
                    synset.insert(0,the_word[:-6])

                # -iness
                elif the_word[-5:]=='iness':
                    # -iness to -y
                    # happiness to happy
                    synset.insert(0,the_word[:-5]+"y")

            # -ies 
            # -es
            if the_word[-2:]=='es':
                if the_word[-3:]=='ies':
                    # -ies to -y
                    synset.insert(0,the_word[:-3]+"y")
                else:
                    # -es to -
                    synset.insert(0,the_word[:-2])
                    # -es to -e
                    synset.append(the_word[:-1])

            # -s to -
            else: 
                synset.insert(0,the_word[:-1])


        if len(the_word)>5:
            if the_word[-5:]=='ation':
                # -ation to -ate
                # accumulation to accumulate
                synset.insert(0,the_word[:-5]+"ate")


        if synset<>[]:
            print "  Trying these: %s"%( ", ".join(synset) )

        return synset

