print "James Joyce - Ulysses"

for im1 in range(18):
    i = im1+1
    filename = "ulysses%d.html"%(i)

    content = ""
    content += "{% extends 'base.html' %}\n"
    content += "{% block title %}Ulysses - &mdash; {{ SITENAME }}{% endblock %}\n"
    content += "{% block content %}\n\n"

    content += "{% include '_includes/"
    content += filename 
    content += "' %}\n\n"

    content += "{% endblock %}\n"


    print "writing html file %s..."%(filename)
    with open(filename,'w') as f:
        f.write(content)

print "done"

