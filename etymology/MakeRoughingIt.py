name = 'roughingit'

#from EtymologyCSV import *
#c = EtymologyCSV(name)
#c.export_word_file()
#c.export_rootlang_file()

from EtymologyChapterHTML import *
h = EtymologyChapterHTML(name)
h.export_html_file()

