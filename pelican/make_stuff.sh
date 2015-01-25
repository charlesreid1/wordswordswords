#!/bin/sh

cd ulysses
python make_ulysses.py
cd ..
cd dubliners
python make_dubliners.py
cd ..
cd frankenstein
python make_frankenstein.py
cd ..
pelican -D content

