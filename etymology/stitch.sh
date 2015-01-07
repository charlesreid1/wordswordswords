#!/bin/sh

DEST="../gh-pages"

cat head.html              > $DEST/copperfield.html
cat key.html              >> $DEST/copperfield.html
cat copperfield_body.html >> $DEST/copperfield.html
cat foot.html             >> $DEST/copperfield.html
cp wordswordswords.css       $DEST/wordswordswords.css

