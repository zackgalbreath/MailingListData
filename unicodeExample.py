#! /usr/bin/env python

from BeautifulSoup import BeautifulStoneSoup
import cgi

def HTMLEntitiesToUnicode(text):
  """Converts HTML entities to unicode.  For example '&amp;' becomes '&'."""
  text = unicode(BeautifulStoneSoup(text, convertEntities=BeautifulStoneSoup.ALL_ENTITIES))
  return text

def unicodeToHTMLEntities(text):
  """Converts unicode to HTML entities.  For example '&' becomes '&amp;'."""
  text = cgi.escape(text).encode('ascii', 'xmlcharrefreplace')
  return text

#text = u'&#1040;&#1088;&#1090;&#1077;&#1084; &#1053;&#1080;&#1082;&#1086;&#1083;&#1072;&#1077;&#1074;&#1080;&#1095;'
text = u'D&#382;enan Zuki&#263;,'

uni = HTMLEntitiesToUnicode(text)

text2 = u'2972'
uni2 = HTMLEntitiesToUnicode(text2)


f = file("blah.txt", "w")
f.write(uni.encode('utf-8'))
f.write(u"\n")
f.write(uni2.encode('utf-8'))
f.close()
print uni
