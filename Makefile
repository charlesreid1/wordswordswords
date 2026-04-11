.PHONY: all etymology pelican-templates pelican clean-etymology clean-pelican clean clean-rendered setup

# Dynamically load books from books.yaml
BOOKS = $(shell python3 -c "import yaml; print(' '.join(yaml.safe_load(open('books.yaml'))))")

PELICAN_THEME_INCLUDES = pelican/cmr-pelican-theme/templates/_includes

all: setup etymology pelican-templates pelican deploy

all-but-deploy: setup etymology pelican-templates pelican

setup:
	@echo "--- Ensuring template directories exist ---"
	mkdir -p $(PELICAN_THEME_INCLUDES)

etymology: setup
	@echo "--- Generating etymology HTML for all books ---"
	python -m etymology.run --book all --step html --mode pipeline

pelican-templates:
	@echo "--- Generating Pelican templates and wrappers ---"
	cd pelican && python make_stuff.py

pelican:
	@echo "--- Building Pelican site ---"
	cd pelican && pelican -s pelicanconf.py

deploy:
	@echo "--- Deploying to gh-pages ---"
	./deploy.sh

clean-rendered:
	@echo "--- Cleaning rendered HTML files ---"
	rm -rf html/*
	rm -rf pelican/generated_templates
	rm -f $(PELICAN_THEME_INCLUDES)/*.html

clean: clean-rendered
	@echo "--- Cleaning Pelican output ---"
	rm -rf pelican/output/*
