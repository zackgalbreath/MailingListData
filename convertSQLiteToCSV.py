#!/usr/bin/env python

from BeautifulSoup import BeautifulStoneSoup
import codecs
import cgi
import sqlite3
import string
import sys

#Converts HTML entities to unicode.  For example '&amp;' becomes '&'
def HTMLEntitiesToUnicode(text):
  text = unicode(BeautifulStoneSoup(text, convertEntities=BeautifulStoneSoup.ALL_ENTITIES))
  return text

if __name__ == "__main__":
  try:
    conn = sqlite3.connect('MailingListData.db')
    c = conn.cursor()
  except sqlite3.Error, e:
    print "Error occurred:", e.args[0]
    sys.exit(1)

  try:
    c.execute("SELECT * FROM MailingListData")
  except sqlite3.Error, e:
    print "Error occurred:", e.args[0]
    sys.exit(1)

  f = file("MailingListData.csv", "w")
  f = codecs.open("MailingListData.csv", "w", "utf-8-sig")

  col_name_list = [tuple[0] for tuple in c.description]
  for col_name in col_name_list:
    f.write(col_name)
    if col_name == col_name_list[-1]:
      f.write("\n")
    else:
      f.write(", ")

  for row in c:
    for field in row:
      #f.write(field)
      #noCommas = string.replace(str(field),","," ")
      #uni = HTMLEntitiesToUnicode(noCommas).encode('utf-8')
      print field
      uni = HTMLEntitiesToUnicode(field).encode('utf-8')
      f.write(uni.encode('utf-8'))
      #f.write(HTMLEntitiesToUnicode(string.replace(str(field),","," ")).encode('utf-8'))

      if field == row[-1]:
        f.write("\n")
      else:
        f.write(", ")

  f.close()
  c.close()
