.PHONY: all etymology pelican-templates pelican clean-etymology clean-pelican clean clean-rendered

BOOKS = frankenstein dubliners ulysses crimeandpunishment roughingit variableman leviathan copperfield treatisegovt

PELICAN_THEME_INCLUDES = pelican/cmr-pelican-theme/templates/_includes

all: etymology pelican-templates pelican

etymology:
	@echo "--- Generating etymology HTML for all books ---"
	python -m etymology.run --book all --step html --mode pipeline

pelican-templates:
	@echo "--- Generating Pelican templates and wrappers ---"
	cd pelican && python make_stuff.py

pelican:
	@echo "--- Building Pelican site ---"
	cd pelican && pelican -s pelicanconf.py

deploy: all
	@echo "--- Deploying to gh-pages ---"
	cd pelican/output && git add . && git commit -m "Host update" && git push origin gh-pages

clean-rendered:
	@echo "--- Cleaning rendered HTML files ---"
	rm -rf html/*
	rm -f $(PELICAN_THEME_INCLUDES)/frankenstein*.html
	rm -f $(PELICAN_THEME_INCLUDES)/dubliners*.html
	rm -f $(PELICAN_THEME_INCLUDES)/ulysses*.html
	rm -f $(PELICAN_THEME_INCLUDES)/crimeandpunishment*.html
	rm -f $(PELICAN_THEME_INCLUDES)/roughingit*.html
	rm -f $(PELICAN_THEME_INCLUDES)/variableman*.html
	rm -f $(PELICAN_THEME_INCLUDES)/leviathan*.html
	rm -f $(PELICAN_THEME_INCLUDES)/copperfield*.html
	rm -f $(PELICAN_THEME_INCLUDES)/treatisegovt*.html

clean: clean-rendered
	@echo "--- Cleaning Pelican output ---"
	rm -rf pelican/output/*
