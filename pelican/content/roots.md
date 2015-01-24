Title: Searching for Word Roots
Date: 2015-01-24 09:00
Category: 

Some of the most recent improvements to the Words Words Words (WWW) code
have been in how it deals with a failure to find a word 
in the Online Etymology Dictionary. Some of these failures
are due to a lack of etymology information (the name 
"Eliza", for example). But other failures are because 
we are looking for a conjugated verb, or a past tense
form, or a noun-made-adverb, etc.

For this reason, we can greatly improve our tag coverage
with a few tricks. This code is in the file
```etymology/EtymologyCSV.py``` in the repository,
and is in the method ```EtymologyCSV::get_root_word```.


```python

def get_root_word(self,the_word):

    print ""
    print "Looking for roots of %s..."%(the_word)

```

I use two methods in my code:

* TextBlob Synsets - this uses the TextBlob library to look for 
    similar words, which often include root words.

* Common Suffixes - this tests for common suffixes, removes them,
    and creates a list of the resulting (possible) root words

## TextBlob Synsets

The first thing to do is to use [TextBlob](http://textblob.readthedocs.org),
a Python library, to search for its "synsets" - sets of similar words.
While these synsets are often scattershot and include a wide range of 
dissimilar words, they can sometimes contain the unconjugated form of a 
verb, or a form without a suffix.

To get the synsets, you have to create a TextBlob word:

```python
In [4]: from textblob import Word

In [7]: w = Word("looking")

In [8]: print w.synsets
[Synset('look.n.02'), Synset('looking.n.02'), Synset('look.v.01'), Synset('look.v.02'), Synset('look.v.03'), Synset('search.v.02'), Synset('front.v.01'), Synset('attend.v.02'), Synset('look.v.07'), Synset('expect.v.03'), Synset('look.v.09'), Synset('count.v.08'), Synset('looking.s.01')]
```

You can see the format of the synsets from the output.
We can get the word by itself using ```.split('.')[0]```:

```python

    try:
        full_synset = Word(the_word).synsets
        full_synset_strings = [syn.name().split('.')[0] for syn in full_synset]
    except:
        full_synset_strings = []
```

Now we need a way of discarding irrelevant words in the synset.
I found the criteria of the first three letters matching was
sufficient for almost every case.

```python
    synset = []
    for sss in zip(full_synset_strings):
        if sss[:3] == the_word[:3]:
            synset.append(sss)
```

## Common Suffixes

The next task to accomplish with the code was removing 
common suffixes to create additional (possible) root words,
which could then be looked up in lieu of the original at the Online
Etymology Dictionary. 

A list of suffixes I checked for:

* ```-ed```
* ```-ing```
* ```-ly```
* ```-es```
* ```-ies```

There are two cases for removing suffixes: preceded by a consonant,
and preceded by a vowel. The consonant case is more common,
so these are added to the beginning of the list of possible root 
words. The vowel cases are added to the end. 

This may seem hacky and may generate a few false positives, 
but it works surprisingly well without being overly intricate.

```python

    # first try removing any common suffixes

    # -ed
    if the_word[-2:]=='ed':
        # -ed to -
        # consonant, more likely, so prepend
        synset.insert(0,the_word[:-2])

        # -ed to -e
        synset.append(the_word[:-1])

    # -ing
    if the_word[-3:]=='ing':
        # -ing to -
        synset.insert(0,the_word[:-3])
        # -gging to -g
        # -nning to -n
        synset.append(the_word[:-4])

    # -ly
    if the_word[-2:]=='ly':
        # -ly to -
        synset.insert(0,the_word[:-2])

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
```

## The Final Step

Once these lists of possible root words have been assembled,
they are returned to the main portion of the code, where 
they are each looked up on the Online Etymology Dictionary.

```python

    if synset<>[]:
        print "  Trying these: %s"%( ", ".join(synset) )

    return synset

```

