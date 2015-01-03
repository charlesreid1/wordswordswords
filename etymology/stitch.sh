#!/bin/sh

DEST="../gh-pages"

cat copperfield_head.html >  $DEST/copperfield.html
cat copperfield_body.html >> $DEST/copperfield.html
cat copperfield_foot.html >> $DEST/copperfield.html
cp copperfield.css           $DEST/copperfield.css

