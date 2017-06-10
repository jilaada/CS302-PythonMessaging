#!/usr/bin/python
""" cherrypy_example.py

	COMPSYS302 - Software Design
	Author: Jilada Eccleston
	Last Edited: 19/02/2015

	This program uses the CherryPy web server (from www.cherrypy.org).
"""
# Requires:  CherryPy 3.2.2  (www.cherrypy.org)
#            Python  (We use 2.7)
# 

import urllib
import json
import time
import sqlite3
import hashlib
from sqlite3 import Error

# =====================
# Database Manipulation
# =====================

# Function that will take a connected database and add the table headers
def createTable():
	sql_create_table_usersRegisters = "CREATE TABLE IF NOT EXISTS userRegister (id INTEGER PRIMARY KEY AUTOINCREMENT, upi TEXT UNIQUE, ip TEXT, public_key TEXT, location INTEGER, last_login TEXT, port TEXT, status TEXT); "
	sql_create_table_messageData = "CREATE TABLE IF NOT EXISTS messageData (id INTEGER PRIMARY KEY AUTOINCREMENT, senderUPI TEXT, destinationUPI TEXT, time_stamp TEXT, message TEXT, message_type TEXT); "
	sql_create_table_profile = "CREATE TABLE IF NOT EXISTS userProfile (id INTEGER PRIMARY KEY AUTOINCREMENT, upi TEXT UNIQUE, fullname TEXT, position TEXT, description TEXT, location TEXT, picture TEXT); "
	sql_create_table_events = "CREATE TABLE IF NOT EXISTS eventData (id INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT , host TEXT, guest TEXT, event_name TEXT, start_time TEXT, end_time TEXT, attendance INTEGER, event_desc TEXT, event_loc TEXT); "
	conn = connectDatabase()
	c = conn.cursor()
	try:
		c.execute(sql_create_table_usersRegisters)
		c.execute(sql_create_table_messageData)
		c.execute(sql_create_table_profile)
		c.execute(sql_create_table_events)
		conn.commit()
	except Error as e:
		print "Error in Database Execution - " + str(e)
	conn.close()
	pass

# Function that will take a connected database and add the registered users to the list
def addRegisteredUsers(userList):
	list = tuple(userList.read().split(","))
	for user in list:
		addUser(user)
	pass

# Function will add single users one at a time to the database
def addUser(user):
	sql_insert_upi = 'INSERT OR IGNORE INTO userRegister(upi) VALUES(?) '
	conn = connectDatabase()
	c = conn.cursor()
	try:
		c.execute(sql_insert_upi, (user,))
		conn.commit()
	except Error as e:
		print "Error in Database Execution - " + str(e)
	conn.close()
	pass


def getUsers():
	sql_select_message = 'SELECT upi FROM userRegister'
	conn = connectDatabase()
	conn.row_factory = sqlite3.Row
	c = conn.cursor()
	try:
		c.execute(sql_select_message)
		userList = c.fetchall()
	except Error:
		print "Error in getting users"
		userList = "0"
	conn.close()
	return userList

# Refresh Database will refresh and add the the activity of existing users in the list
def refreshDatabase(onlineUsers):
	dic = json.loads(onlineUsers)
	conn = connectDatabase()
	c = conn.cursor()
	for items in dic:
		try:
			sql_update_pubkey = 'UPDATE userRegister SET public_key==:publickey WHERE upi==:username'
			c.execute(sql_update_pubkey, {"publickey": dic[items]['publicKey'], "username": dic[items]['username']})
			conn.commit()
		except KeyError:
			try:
				sql_update_user = 'UPDATE userRegister SET ip==:ip, location==:location, last_login==:lastLogin, port==:port WHERE upi==:username'
				c.execute(sql_update_user, {"ip": dic[items]['ip'], "location": dic[items]['location'],
				                            "lastLogin": dic[items]['lastLogin'], "username": dic[items]['username'],
				                            "port": dic[items]['port']})
				conn.commit()
			except (KeyError, TypeError) as e:
				print e
	conn.close()
	return dic

def pingRefresh(sender):
	conn = connectDatabase()
	c = conn.cursor()
	epochtime = float(time.time())
	try:
		sql_update_user = 'UPDATE userRegister SET last_login==:time WHERE upi==:username'
		c.execute(sql_update_user, {"time":epochtime, "username":sender})
	except KeyError as e:
		print e
		conn.close()
		return 1
	conn.commit()
	conn.close()
	return 0

# Refresh the message database so that messages are stored in teh database
# Need to add stuff to do with the hashing etc.
def insertMessage(messageData):
	conn = connectDatabase()
	c = conn.cursor()
	try:
		# Assuming they are not 
		sql_select_message = 'SELECT * FROM messageData WHERE senderUPI==:username AND time_stamp==:time_stamp'
		c.execute(sql_select_message, {"username":messageData['sender'], "time_stamp":messageData['stamp']})
		if c.fetchone() is None:
			try:
				sql_insert_message = 'INSERT INTO messageData (senderUPI, time_stamp, message, destinationUPI, message_type) VALUES (:username, :time_stamp, :message, :destination, :type)'
				c.execute(sql_insert_message, {"username":messageData['sender'], "time_stamp":messageData['stamp'], "message":messageData['message'], "destination":messageData['destination'], "type":'text/plain'})
				conn.commit()
			except (KeyError, TypeError) as e:
				print e
				conn.close()
				return 1
			except Error as e:
				print e
				conn.close()
				return 4
		else:
			print "Message saved already"
	except Error as e:
		print e
		return 4
	conn.close()
	return 0


# Store the file messages on the database
def storeFile(fileData):
	conn = connectDatabase()
	c = conn.cursor()
	try:
		sql_select_message = 'SELECT * FROM messageData WHERE senderUPI==:username AND time_stamp==:time_stamp AND message_type==:type'
		c.execute(sql_select_message, {"username":fileData['sender'], "time_stamp":fileData['stamp'], "type":fileData['content_type']})
		if c.fetchone() is None:
			try:
				sql_insert_message = 'INSERT INTO messageData (senderUPI, time_stamp, message, destinationUPI, message_type) VALUES (:username, :time_stamp, :message, :destination, :type)'
				c.execute(sql_insert_message, {"username":fileData['sender'], "time_stamp":fileData['stamp'], "message":fileData['filename'], "destination":fileData['destination'], "type":fileData['content_type']})
				conn.commit()
			except (KeyError, TypeError) as e:
				print e
				conn.close()
				return 1
			except Error as e:
				print e
				conn.close()
				return 4
		else:
			print "Message saved already"
	except Error as e:
		print e
		return 4
	conn.close()
	return 0


# Get the IP from the database
def getIP(destUPI):
	conn = connectDatabase()
	conn.row_factory = sqlite3.Row
	c = conn.cursor()
	try:
		sql_select_ip = 'SELECT ip, port FROM userRegister WHERE upi==:upi'
		c.execute(sql_select_ip, {"upi":destUPI})
		getIP = c.fetchone()
		conn.close()
		if getIP is None:
			return 0
		else:
			return getIP
	except Error as e:
		print "Error - Not able to print get name"
		conn.close()
		return 0


# Get all the messages sent to and from a person
def getMessages(user, clientUser):
	conn = connectDatabase()
	conn.row_factory = sqlite3.Row
	c = conn.cursor()
	try:
		sql_select_messages = 'SELECT senderUPI, time_stamp, message, message_type FROM messageData WHERE (senderUPI==:user AND destinationUPI==:client) OR (senderUPI==:client AND destinationUPI==:user)'
		c.execute(sql_select_messages, {"user":user, "client":clientUser})
		messagesReturn = c.fetchall()
		conn.close()
	except Error as e:
		print e
		conn.close()
		messagesReturn = 0
	return messagesReturn

# Get a list of users who are online
def dropdownGet():
	# Getting comparison time
	currentTime = time.time()
	compTime = currentTime - 60
	# Connect to database
	conn = connectDatabase()
	conn.row_factory = sqlite3.Row
	c = conn.cursor()
	try:
		sql_select_onlineUsers = 'SELECT upi FROM userRegister WHERE last_login >= :time'
		c.execute(sql_select_onlineUsers, {"time":compTime})
		userList = c.fetchall()
		conn.close()
		try:
			# Convert list to tuple
			userList = [i for sub in userList for i in sub]
			return userList
		except Error as e:
			print "Error - in converting tuple to list"
	except Error as e:
		print "Error - not able to get users"
	conn.close()
	return 0


# Store the profile values into the database
def storeProfile(profileData, upi):
	profileData = json.loads(profileData)
	conn = connectDatabase()
	conn.row_factory = sqlite3.Row
	c = conn.cursor()
	try:
		# Try assumes that the profile does not already exist
		sql_insert_profile = 'INSERT INTO userProfile(upi, fullname, position, description, location, picture) VALUES(:upi,:fname,:pos,:desc,:loc,:pic)'
		c.execute(sql_insert_profile, {"upi":upi, "fname":profileData['fullname'], "pos":profileData['position'], "desc":profileData['description'], "loc":profileData['location'], "pic":profileData['picture']})
		conn.commit()
		conn.close()
	except Error as e:
		try:
			sql_update_profile = 'UPDATE userProfile SET fullname = :fullname, position = :pos, description = :desc, location = :loc, picture = :pic WHERE upi==:upi'
			c.execute(sql_update_profile, {"upi": upi, "fullname": profileData['fullname'], "pos": profileData['position'],
		                               "desc": profileData['description'], "loc": profileData['location'],
		                               "pic": profileData['picture']})
			conn.commit()
			conn.close()
		except Error as e:
			print e
			return 1
	conn.close()
	return 0



def storeStatus(status_in, user):
	try:
		status = json.loads(status_in)
		conn = connectDatabase()
		c = conn.cursor()
		try:
			sql_update_status = 'UPDATE userRegister SET status = :stat WHERE upi==:upi'
			c.execute(sql_update_status, {"upi":user, "stat":status['status']})
			conn.commit()
			conn.close()
		except Error as e:
			conn.close()
			print str(e)
	except ValueError as e:
		print str(e)
	except Error as e:
		print str(e)


def getStatus(user):
	conn = connectDatabase()
	conn.row_factory = sqlite3.Row
	c = conn.cursor()
	try:
		sql_update_status = 'SELECT status FROM userRegister WHERE upi==:upi'
		c.execute(sql_update_status, {"upi":user})
		status = c.fetchone()
		return status['status']
	except Error as e:
		return "0"


def getProfile(user):
	conn = connectDatabase()
	conn.row_factory = sqlite3.Row
	c = conn.cursor()
	try:
		sql_select_profile = 'SELECT * FROM userProfile WHERE upi=:user'
		c.execute(sql_select_profile, {"user":user})
		profile = c.fetchone()
		conn.close()
		return profile
	except (KeyError, TypeError) as e:
		print "Error - " + e
		conn.close()
		return 0


def addEvent(eventDict, host):
	conn = connectDatabase()
	c = conn.cursor()
	eventID = hashlib.sha256(eventDict['event_name'] + str(eventDict['start_time'])).hexdigest()
	try:
		sql_insert_event = 'INSERT INTO eventData(event_id, host, guest, event_name, start_time, end_time, attendance, event_desc, event_loc) VALUES(:event_id, :host, :guest, :name, :start, :end, :attend, :desc, :loc)'
		c.execute(sql_insert_event, {	"event_id":eventID, 
										"host":host, 
										"guest":eventDict['guest'], 
										"name":eventDict['event_name'], 
										"start":eventDict['start_time'], 
										"end":eventDict['end_time'], 
										"attend":eventDict['attendance'], 
										"desc":eventDict['event_desc'], 
										"loc":eventDict['event_loc']})
		conn.commit()
		conn.close()
	except Error as e:
		print str(e)
	conn.close()
	return 0


def updateEvent(acknow):
	conn = connectDatabase()
	c = conn.cursor()
	eventID = hashlib.sha256(acknow['event_name'] + str(acknow['start_time'])).hexdigest()
	try:
		sql_update_event = 'UPDATE eventData SET attendance = :attend WHERE event_id==:id AND guest==:sender'
		c.execute(sql_update_event, {"attend":acknow['attendance'], "id":eventID, "sender":acknow['sender']})
		conn.commit()
		conn.close()
	except Exception as e:
		print str(e)
		return 1
	conn.close()
	return 0


def gatherEvents(currentUser, toggle):
	conn = connectDatabase()
	conn.row_factory = sqlite3.Row
	c = conn.cursor()
	epoch = time.time()
	try:
		# Get all distinct events with people
		if toggle == 0:
			sql_select_events = 'SELECT * FROM eventData WHERE (start_time >= :currTime OR end_time >= :currTime) AND host!=:user'
			c.execute(sql_select_events, {"currTime":epoch, "user":currentUser})
		else:
			sql_select_events = 'SELECT * FROM eventData WHERE (start_time >= :currTime OR end_time >= :currTime) AND host==:user'
			c.execute(sql_select_events, {"currTime":epoch, "user":currentUser})
		eventList = c.fetchall()
		conn.close()
		return eventList
	except Exception as e:
		print str(e)
		return 1


def updateAttendance(attendance, row_id):
	conn = connectDatabase()
	c = conn.cursor()
	try:
		sql_update_event = 'UPDATE eventData SET attendance = :attend WHERE id==:rowid '
		c.execute(sql_update_event, {"attend":attendance, "rowid":row_id})
		conn.commit()
		print "here"
		try:
			conn.row_factory = sqlite3.Row
			sql_select_event = 'SELECT host, event_name, start_time FROM eventData WHERE id==:rowid'
			c.execute(sql_select_event, {"rowid":row_id})
			host = c.fetchone()
			return host
		except Exception as e:
			print str(e)
	except Exception as e:
		print str(e)
	return 0


# Connect to the database, returns the connection object
def connectDatabase():
	try:
		conn = sqlite3.connect("database.db")
	except Error as e:
		return e
	return conn
