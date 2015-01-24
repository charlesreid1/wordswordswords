dubliners_stories = ['The Sisters',
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

links = {}

for im1,story in enumerate(dubliners_stories):
    i = im1+1

    filename_base = "dubliners%d"%(i)
    html_filename = filename_base+".html"
    md_filename   = filename_base+".md"

    contents  = "Title: "+story
    contents += "\nAuthors: James Joyce"
    contents += "\nHeaderStyle: languagekey"
    contents += "\nsave_as: "+html_filename
    contents += "\n\n"
    contents += "{%include_html "+html_filename+"%}"
    contents += "\n\n"

    links[story] = html_filename

    with open(md_filename,'w') as f:
        f.write(contents)
    print "Finished writing markdown file ",md_filename





# now make the main page

filename_base = "dubliners"
html_filename = filename_base+".html"
md_filename   = filename_base+".md"
contents  = "Title: Dubliners"
contents += "\nAuthors: James Joyce"
contents += "\nHeaderStyle: book"
contents += "\nsave_as: "+html_filename
contents += "\n\n"

for linkname,link in zip(links.keys(),links.values()):

    #contents += "[" + linkname + "](" + link + ")"
    contents += '<a class="btn btn-large btn-primary" href="'+link+'">'+linkname+'</a>'
    contents += "\n"

contents += "\n\n"

with open(md_filename,'w') as f:
    f.write(contents)
print "Finished writing markdown file ",md_filename


