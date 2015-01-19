from EtymologyCSV import *
c = EtymologyCSV('copperfield')
c.export_word_file()
c.export_rootlang_file()

from EtymologyChapterHTML import *
h = EtymologyChapterHTML('copperfield')
h.export_html_file()
