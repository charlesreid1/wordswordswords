Nchapters = 10

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

    with open(md_filename,'w') as f:
        f.write(contents)
    print "Finished writing markdown file ",md_filename

