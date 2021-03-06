Title: Creating New Pelican Templates
Date: 2015-01-24 09:00
Category: 

The Words Words Words (WWW) library uses the Online Etymology Dictionary and HTML to color-tag
each word in a body of text based on its etymology and root language.
This means that the output of the WWW scripts is usually a directory
full of HTML files (one HTML file per chapter).

I had to figure out what to do with this HTML, and how to embed it in Pelican pages.
(Pelican is the Python static content generator that I am using to create the 
WWW project page.)

## The Plugin Approach

I began by writing a Pelican plugin that would allow me to use Liquid tags to include
HTML files into a Markdown document, like this:

```
{% include_html 'some_html_file.html' %}
```

The problem with this approach, though, is that the plugin basically imports
the HTML file as one big string in the final Markdown document, storing it 
in memory as the rest of the document is constructed. 
But this makes the plugin approach unbearably slow.  
Generating the website content with more than one book would take
upwards of an hour. Minor changes required re-making the site each time.
This was not an acceptable or scalable solution, since my goal was to add
a large number of books.

## The Template Approach

I hit upon a solution when I delved into the template features of Pelican.
Pelican allows you to define new templates, and you can inject large 
HTML documents directly using Jinja templating syntax. This means you can
create a template like ```dummy.html``` in the ```templates/``` directory
of your theme, and insert HTML documents using include statements:

```
{% include '_includes/some_html_file.html' %}
```

Then you can edit your ```pelicanconfig.py``` file to tell Pelican about your
new template:

```
TEMPLATE_PAGES = {}
TEMPLATE_PAGES['dummy.html'] = 'custom/path/to/dummy/index.html'
```

The key is the name of the template file; the value is the 
custom URL path that you want the template to have.

## The Pelican Solution

I still had a problem, however, that a given book might have
upwards of 50 chapters, meaning 50 HTML files. Still not a 
scalable solution.

But Python came to the rescue! I was able to use Python to 
accomplish three tasks:

* Create a Python script to automatically create a new HTML template 
    file for each book chapter;
* Create a central index file for each book, with buttons for each book chapter;
* Populate the ```TEMPLATE_PAGES``` dictionary automatically.

This last bullet is possible, because the config file is 
written in... Python!

## Creating HTML Template Files

In my templates directory, I have a script that automatically 
creates an HTML file that has the theme's header and footer,
and populates the page content with the HTML files 
generated by WWW scripts. Here is my script ```make_dubliners.py```,
for creating pages for each chapter of James Joyce's Dubliners:

```python
for im1 in range(15):
    i = im1+1
    filename = "dubliners%d.html"%(i)

    content = ""
    content += "{% extends 'base.html' %}\n"
    content += "{% block title %}Dubliners - &mdash; {{ SITENAME }}{% endblock %}\n"
    content += "{% block content %}\n\n"

    content += "{% include '_includes/"
    content += filename 
    content += "' %}\n\n"

    content += "{% endblock %}\n"


    print "writing html file %s..."%(filename)
    with open(filename,'w') as f:
        f.write(content)

print "done"

```

## Populating TEMPLATE_PAGES

Here is how I automatically populated the ```TEMPLATE_PAGES``` 
variable for James Joyce's book Dubliners:

```python
TEMPLATE_PAGES['dubliners.html'] = 'dubliners/index.html'
for im1 in range(15):
    i = im1+1
    key = 'dubliners%d.html'%(i)
    val = 'dubliners/%d/index.html'%(i)
    TEMPLATE_PAGES[key] = val
```













