
#Main file
import mechanize
import re
import sqlite3
from twilio.rest import TwilioRestClient
import twilio

USERNAME = 'MySchool Username'
PASSWORD = 'MySchool Password'
TWILIOID = 'Twilio Account ID'
TWILIOTOKEN = 'Twilio Token'
TWILIONUMBER = 'Twilio Phone Number'
MYPHONENUMBER = 'My Phone Number'
SCHOOLURL = "https://MYSCHOOLSITE.com"

def main():

	#Initial Connection to the DB
	conn = openDBconn()

	#DB has already been initiated with the following code the first time
	'''
	curs = getDBCursor(conn)
	curs.execute("CREATE TABLE Classes (ClassID Integer PRIMARY KEY, Classname text)")
	curs.execute("CREATE TABLE Announcements (AID Integer PRIMARY KEY, ClassID Integer, Announcement text, URL text, FOREIGN KEY (ClassID) REFERENCES Classes(ClassID))")
	curs.execute("INSERT INTO Classes(ClassID, Classname) VALUES (5893, 'CIS 530 - Artificial Intelligence')")
	curs.execute("INSERT INTO Classes(ClassID, Classname) VALUES (8015, 'CIS 530 - Artificial Intelligence')")
	curs.execute("INSERT INTO Classes(ClassID, Classname) VALUES (11301, 'CIS 520 - Operating Systems')")
	curs.execute("INSERT INTO Classes(ClassID, Classname) VALUES (12402, 'CIS 505 - Programming Paradigms')")
	curs.execute("INSERT INTO Classes(ClassID, Classname) VALUES (2415, 'CIS 498 - Big Data')")
	curs.execute("INSERT INTO Classes(ClassID, Classname) VALUES (8664, 'ENG 516 - Written Communication for the Sciences')")
	curs.close()
	'''
	
	#Setting up mechanize browser object and opening CANVAS login page
	browser = setUpBrowser()
	response = browser.open(SCHOOLURL)

	#Selects the log in form, and submits the form with the particular username and password
	browser.select_form(nr=2)
	browser.form['username'] = USERNAME
	browser.form['password'] = PASSWORD
	browser.submit()

	#Iterating over the links in the page which have 'announcements' in 
	#the url text
	
	regexp = re.compile('/courses/([0-9]+)/announcements/([0-9]+)')

	#Main Activity Loop of the program
	for l in browser.links(url_regex = regexp):
		matcher = re.search(regexp, l.url)
		announcementID = int(matcher.group(2))
		if not isannouncementinDB(announcementID, conn) :
			
			classID = int(matcher.group(1))
			url = l.base_url[:-1]+l.url
			text = l.text

			#Adding announcement to the DB
			addAnnouncementToDB(announcementID, classID, text, url, conn)
			
			#Sending Message with the class, text and URL of the announcement
			sendText(classID, text, url, conn)
	
	closeCommitDB(conn)

'''
Uses mechanize to set up the browser to open a connection to the page
'''
def setUpBrowser():

	browser = mechanize.Browser()
	browser.set_handle_robots(False)
	browser.addheaders = [('User-agent', 'Firefox')]
	return browser
'''
Checks the DB to see if there is a row with the AnnouncementID = aid.
AnnouncementIDs are unique.
'''

def isannouncementinDB(aid, conn):
	curs = getDBCursor(conn)
	curs.execute("SELECT count(*) FROM Announcements WHERE AID = ?", (aid,))
	existcheck = curs.fetchone()[0]
	curs.close()

	if existcheck == 0 :
		return False
	else :
	 	return True

'''
Takes a connection object as a parameter and returns a cursor object
which can be used to execute SQL statements.
'''

def getDBCursor(conn):
	curs = conn.cursor()
	return curs
'''
Sets up the initial connection to the already existing DB that
lasts for the entirety of this run of the program.
'''

def openDBconn():
	conn = sqlite3.connect('./project.db')
	return conn

'''
Commits any changes and closes the connection to the DB at the end of 
this cycle of the program.
'''

def closeCommitDB(conn):
	conn.commit()
	conn.close()

'''
Takes in the ClassID as a parameter and queries the 'Classes' table in
the DB and returns the name of the class as a string.
'''

def retrieveClass(cid, conn):
	curs = getDBCursor(conn)
	
	curs.execute("SELECT Classname FROM Classes WHERE ClassID = ?", (cid,))
	
	className = curs.fetchone()[0]
	curs.close()

	if className is not None : return className
	else : return 0

'''
Creates a Twilio Rest Client and other information pertaining to the
announcement and sends a text message to the specified phone number
with the class name, text and the url of the announcement.
'''	

def sendText(classid, text, url, conn):
	classname = retrieveClass(classid, conn)

	try :
		client = twilio.rest.TwilioRestClient(TWILIOID, TWILIOTOKEN)
		message = client.messages.create(
			body = "Class : "+classname+"\nText : "+text+"\n URL : "+url+"\n",	
			to = MYPHONENUMBER,
			from_ = TWILIONUMBER
			)
		

	except twilio.TwilioRestException as e:
		f = open('C:/Users/USERNAME/Desktop/twilio project/log.txt', 'w')
		f.write(e)
		f.close()
'''
Adds the announcement to the DB, a check to make sure the announcement
does nto exist in the DB has already been performed before this method
is called
'''

def addAnnouncementToDB(aid, classid, text, url, conn):
	curs = getDBCursor(conn)
	curs.execute("INSERT INTO Announcements(AID, ClassID, Announcement, URL) VALUES (?, ?, ?, ?)", (aid, classid, text, url))
	curs.close()

if __name__=="__main__": main()
