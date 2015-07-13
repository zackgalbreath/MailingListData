#!/usr/bin/env python
import re
import pycurl
import sqlite3
import string
import StringIO
import sys

#Determines whether or not a message had a meaningful attachment
def messageHasAttachment(contents):
  if contents.find("non-text attachment was scrubbed...") == -1:
    return "no"
  if contents.count("non-text attachment was scrubbed") == \
    contents.count("pgp-signature"):
    return "no"
  return "yes"

#Extracts metadata from a single message
def parseURL(URL):
  messageData = {}

  buffer = StringIO.StringIO()
  curl = pycurl.Curl()
  curl.setopt(pycurl.URL, "%s" % URL)
  curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
  curl.perform()
  curl.close()

  contents = buffer.getvalue()
  messageData["length"] = len(contents)

  messageData["attachment"] = messageHasAttachment(contents)

  dateTimeRE = re.compile("<I>([a-zA-Z]+).*?([0-9:]{8})")
  match = dateTimeRE.search(contents)
  messageData["day"] = match.group(1)
  messageData["time"] = match.group(2)

  return messageData

if __name__ == "__main__":

  #create an empty database with the appropriate columns
  #note that this deletes your old database file, so move it
  try:
    conn = sqlite3.connect('MailingListData.db')
    sqlite = conn.cursor()
    sqlite.execute("DROP TABLE MailingListData")
    sqlite.execute("CREATE TABLE MailingListData(Message_Subject TEXT, Author TEXT, Received_Reply TEXT, Time_of_Day TEXT, Day_of_Week TEXT, Message_Length INTEGER, Any_Attachments TEXT, Archive_URL TEXT)")
  except sqlite3.Error, e:
    print "Error 1 occurred:", e.args[0]
    sys.exit(1)

  #initialize our data structure.
  #This will contain data about the messages that we parse.
  subjects = {}

  #regular expression to get subject
  subjectRE = re.compile(r"HREF=\"(.*?)\">\[Insight-users\]\s(.*)$")
  #regular expression to get author
  authorRE = re.compile(r"<I>(.*)$")

  baseURL = "http://www.itk.org/pipermail/insight-users/2011-August/"

  #use cURL to get a list of messages to parse
  listURL = "http://www.itk.org/pipermail/insight-users/2011-August/thread.html"
  buffer = StringIO.StringIO()
  curl = pycurl.Curl()
  curl.setopt(pycurl.URL, "%s" % listURL)
  curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
  curl.perform()
  curl.close()

  #parse the list of messages
  contents = buffer.getvalue().split('\n');
  for i in range(0,len(contents)):
    line = contents[i]

    #skip lines that don't contain data about messages sent to the mailing list
    if line.find("[Insight-users]") == -1:
      continue

    #get the subject of this message
    match = subjectRE.search(line)
    URL = baseURL + match.group(1)
    subject = string.replace(match.group(2), "\t", " ")

    #get the author of this message (two lines later)
    i = i + 2
    line = contents[i]
    match = authorRE.search(line)
    #unicode is fun
    author = match.group(1)

    #is this a reply to a message that we've already seen?
    if subject in subjects:
      messageData = subjects[subject]
      #is it still waiting for a proper reply?
      if messageData["reply"] != "yes":
        #is the reply from the original author?
        if messageData["author"] == author:
          messageData["reply"] = "self only"
        else:
          messageData["reply"] = "yes"

    else:
      messageData = parseURL(URL)
      messageData["author"] = author
      messageData["URL"] = URL
      messageData["reply"] = "no"
      subjects[subject] = messageData

  try:
    for subject, data in subjects.items():
      #reorganize the data into the list that SQLite expects
      row = [subject, data["author"], data["reply"], data["time"], data["day"], data["length"], data["attachment"], data["URL"]]
      #sqlite.execute("INSERT INTO MailingListData(Model, Perturbation, Initialization_Time, Forecast_Hour, Handle) VALUES(?,?,?,?,?)", r)
      print row
      sqlite.execute("INSERT INTO MailingListData(Message_Subject, Author, Received_Reply, Time_of_Day, Day_of_Week, Message_Length, Any_Attachments, Archive_URL) VALUES(?,?,?,?,?,?,?,?)", row)
      conn.commit()
  except sqlite3.Error, e:
    print "Error 2 occurred:", e.args[0]
    sys.exit(1)

  try:
    sqlite.execute("SELECT * FROM MailingListData")
  except sqlite3.Error, e:
    print "Error 1 occurred:", e.args[0]
    sys.exit(1)
  for row in sqlite:
    print row
  sqlite.close()

