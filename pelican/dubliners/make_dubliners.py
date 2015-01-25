print "James Joyce - Dubliners"

for im1 in range(15):
    i = im1+1
    templatename = "jjdu%d.html"%(i)
    filename = "dubliners%d.html"%(i)

    content = ""
    content += "{% extends 'base.html' %}\n"
    content += "{% block title %}Dubliners - &mdash; {{ SITENAME }}{% endblock %}\n"
    content += "{% block content %}\n\n"

    content += "{% include '_includes/"
    content += filename 
    content += "' %}\n\n"

    content += "{% endblock %}\n"


    print "writing file %s --> %s..."%(templatename,filename)
    with open(templatename,'w') as f:
        f.write(content)

print "done"

