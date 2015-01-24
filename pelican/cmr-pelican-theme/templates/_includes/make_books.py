from bs4 import BeautifulSoup as BS



books = {}
books['dubliners.html'] = 'Dubliners, by James Joyce'
books['copperfield.html'] = 'David Copperfield, by Charles Dickens'



# html.parser via http://stackoverflow.com/questions/14822188/dont-put-html-head-and-body-tags-automatically-beautifulsoup
soup = BS('''<div class="well">
        <div>
        <h1>Tagged Books</h1>
        </div>
        </div>''',"html.parser")
# we need 2 div tags, 
# so we can manipulate tags
# with beautifulsoup.
# (dumb...)


# grab second div tag 
# (contains everything interesting)
divtag = soup.find_all('div')[1]

# create our modified div tag
divtag_mod = divtag



# grab first (only) h1 tag
# and wrap it in a p tag
p_tag = soup.new_tag('p')
h1tag = soup.find_all('h1')[0]
p_tag.append(h1tag)

# append this to the soup
divtag_mod.append(p_tag)



# now construct title/buttons for each book

for link,book in zip(books.keys(),books.values()):

    print "Making buttons for book:",book

    # make tag for book title
    p_tag = soup.new_tag('p')
    title_tag = soup.new_tag('h2')
    title_tag.string = book
    p_tag.append(title_tag)

    # put it in
    divtag_mod.append(p_tag)

    # make button for each chapter
    btn_tag = soup.new_tag('a')
    btn_tag['href'] = link
    btn_tag['class'] = 'btn btn-large btn-success'
    btn_tag.string = "See this book's etymology"

    p_tag.append(btn_tag)
    divtag_mod.append(p_tag)

    print "done"

filename = "books.html"

print "Saving results..."
with open(filename,'w') as f:
    f.write(soup.prettify())
print "done"


