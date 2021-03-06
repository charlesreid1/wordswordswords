title = "Dubliners"
author = "James Joyce"
name = "dubliners"
short = "jjdu"
chapters = ['The Sisters',
            'An Encounter',
            'Araby',
            'Eveline',
            'After the Race',
            'Two Gallants',
            'The Boarding House',
            'A Little Cloud',
            'Counterparts',
            'Clay',
            'A Painful Case',
            'Ivy Day in the Committee Room',
            'A Mother',
            'Grace',
            'The Dead']

print author + " - " + title




# write the template file, which contains
# a Jinja wrapper for the tagged HTML file
for im1,chapter in enumerate(chapters):
    i = im1+1

    templatename = "%s%d.html"%(short,i)
    filename = "%s%d.html"%(name,i)

    content = ""
    content += "{% extends 'bookbase.html' %}\n"
    content += "{% block title %}"
    content += title
    content += " &mdash; {{ SITENAME }}{% endblock %}\n"
    content += "{% block content %}\n\n"

    content += "{% include '_includes/"
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


for ichm1,chapter in enumerate(chapters):
    ich = ichm1+1

    link = "%d/index.html"%(ich)
    linkname = "%d &mdash; %s"%(ich,chapter)
    content += '<p>'
    content += '<a class="btn btn-large btn-primary" href="'+link+'">'+linkname+'</a>'
    content += '</p>'
    content += "\n\n"

content += "{% endblock %}\n"

content += "\n\n"

print "writing index file %s..."%(indexname)
with open(indexname,'w') as f:
    f.write(content)

