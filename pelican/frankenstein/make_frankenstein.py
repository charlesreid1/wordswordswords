title = "Frankenstein"
author = "Mary Shelley"
name = "frankenstein"
short = "msfr"
chapters = []
for im1 in range(4):
    i = im1+1
    chapters.append("Letter %d"%(i))
for jm1 in range(24):
    j = jm1+1
    chapters.append("Chapter %d"%(j))

print author + " - " + title




# write the template file, which contains
# a Jinja wrapper for the tagged HTML file
for im1,chapter in enumerate(chapters):
    i = im1+1

    templatename = "%s%d.html"%(short,i)
    filename = "%s%d.html"%(name,i)

    content = ""
    content += "{% extends 'base.html' %}\n"
    content += "{% block title %}"
    content += title
    content += " - &mdash; {{ SITENAME }}{% endblock %}\n"
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
content += " - &mdash; {{ SITENAME }}{% endblock %}\n"
content += "{% block content %}\n\n"


for ichm1,chapter in enumerate(chapters):
    ich = ichm1+1

    link = "%s/%d/index.html"%(name,ich)
    linkname = chapter
    content += '<p>'
    content += '<a class="btn btn-large btn-primary" href="'+link+'">'+linkname+'</a>'
    content += '</p>'
    content += "\n\n"

content += "{% endblock %}\n"

content += "\n\n"

print "writing index file %s..."%(indexname)
with open(indexname,'w') as f:
    f.write(content)

