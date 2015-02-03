import os.path
from bs4 import BeautifulSoup


title = "Roughing It"
author = "Mark Twain"
name = "roughingit"
short = "mtri"
chapters = []
filenames = []



nfiles = len(os.listdir('_include'))

for jm1 in range(nfiles):
    j = jm1+1

    print "-"*20
    print "chapter id: %d"%(j)

    filename = "_include/%s%d.html"%(name,j)
    print "chapter file: %s"%(filename)

    filenames.append(filename)

    with open(filename,'r') as f:
        soup = BeautifulSoup(f.read())

        chapter_name = soup.find_all('h2')[0].get_text()
        chapters.append(chapter_name)

        print "chapter title: %s"%(chapter_name)

print author + " - " + title




# write the template file, which contains
# a Jinja wrapper for the tagged HTML file
for im1,(chapter,filename) in enumerate(zip(chapters,filenames)):
    i = im1+1

    templatename = "%s%d.html"%(short,i)

    content = ""
    content += "{% extends 'bookbase.html' %}\n"
    content += "{% block title %}"
    content += chapter
    content += " &mdash; {{ SITENAME }}{% endblock %}\n"
    content += "{% block content %}\n\n"

    content += "{% include '"
    content += filename 
    content += "' %}\n\n"

    content += "{% endblock %}\n"


    print "writing file %s (wrapping %s)..."%(templatename,filename)
    with open(templatename,'w') as f:
        f.write(content)



# write the book index file
# (url schema: chapter X at /bookname/X/index.html)
indexname = "%s.html"%(short)

content = ""
content += "{% extends 'base.html' %}\n"
content += "{% block title %}"
content += title
content += " &mdash; {{ SITENAME }}{% endblock %}\n"
content += "{% block content %}\n\n"

content += "<h1>%s</h1>\n\n"%(title)
content += "<h2>%s</h2>\n\n"%(author)

content += "<p>&nbsp;</p>\n"
content += "<hr />\n"
content += "<p>&nbsp;</p>\n"



for ichm1,(chapter,filename) in enumerate(zip(chapters,filenames)):

    ich = ichm1+1

    link = "%d/index.html"%(ich)
    linkname = "%s"%(chapter)
    content += '<p>'
    content += '<a class="btn btn-large btn-primary" href="'+link+'">'+linkname+'</a>'
    content += '</p>'
    content += "\n\n"

content += "{% endblock %}\n"

content += "\n\n"

print "writing index file %s..."%(indexname)
with open(indexname,'w') as f:
    f.write(content)

