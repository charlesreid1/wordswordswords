chapters = ['Telemachus',
            'Nestor',
            'Proteus',
            'Calypso',
            'Lotus Eaters',
            'Hades',
            'Aeolus',
            'Lestrygonians',
            'Scylla and Charybdis',
            'Wandering Rocks',
            'Sirens',
            'Cyclops',
            'Nausicaa',
            'Oxen of the Sun',
            'Circe',
            'Eumaeus',
            'Ithaca',
            'Penelope']

links = {}

for im1,chapter in enumerate(chapters):
    i = im1+1

    filename_base = "ulysses%d"%(i)
    html_filename = filename_base+".html"
    md_filename   = filename_base+".md"

    contents  = "Title: "+chapter
    contents += "\nAuthors: James Joyce"
    contents += "\nHeaderStyle: languagekey"
    contents += "\nsave_as: "+html_filename
    contents += "\n\n"
    contents += "{%include_html "+html_filename+"%}"
    contents += "\n\n"

    links[chapter] = html_filename

    with open(md_filename,'w') as f:
        f.write(contents)
    print "Finished writing markdown file ",md_filename





# now make the main page

filename_base = "ulysses"
html_filename = filename_base+".html"
md_filename   = filename_base+".md"
contents  = "Title: Ulysses"
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



