Nchapters = 10

links = {}

for im1 in range(Nchapters):
    i = im1+1

    filename_base = "copperfield%d"%(i)
    html_filename = filename_base+".html"
    md_filename   = filename_base+".md"

    contents  = "Title: David Copperfield, Chapter %d"%(i)
    contents += "\nAuthors: Charles Dickens"
    contents += "\nHeaderStyle: languagekey"
    contents += "\nsave_as: "+html_filename
    contents += "\n\n"
    contents += "{%include_html "+html_filename+"%}"
    contents += "\n\n"

    key = "Chapter %d"%(i)
    links[key] = html_filename

    with open(md_filename,'w') as f:
        f.write(contents)
    print "Finished writing markdown file ",md_filename






# now make the main copperfield page

filename_base = "copperfield"
html_filename = filename_base+".html"
md_filename   = filename_base+".md"
contents  = "Title: David Copperfield"
contents += "\nAuthors: Charles Dickens"
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

