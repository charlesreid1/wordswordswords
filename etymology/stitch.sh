#!/bin/sh

DEST="../gh-pages"

cat head.html              > $DEST/copperfield.html
cat key.html              >> $DEST/copperfield.html
cat copperfield_body.html >> $DEST/copperfield.html
cat foot.html             >> $DEST/copperfield.html

cat head.html              > $DEST/dubliners.html
cat key.html              >> $DEST/dubliners.html
cat dubliners_body.html   >> $DEST/dubliners.html
cat foot.html             >> $DEST/dubliners.html

#cat head.html           > $DEST/small.html
#cat key.html           >> $DEST/small.html
#cat small_body.html    >> $DEST/small.html
#cat foot.html          >> $DEST/small.html

cp wordswordswords.css    $DEST/wordswordswords.css

