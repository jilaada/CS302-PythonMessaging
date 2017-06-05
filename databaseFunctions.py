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
from sqlite3 import Error

# =====================
# Database Manipulation
# =====================

# Function that will take a connected database and add the table headers
def createTable():
	sql_create_table_usersRegisters = "CREATE TABLE IF NOT EXISTS userRegister (id INTEGER PRIMARY KEY AUTOINCREMENT, upi TEXT UNIQUE, ip TEXT, public_key TEXT, location INTEGER, last_login TEXT, port TEXT); "
	sql_create_table_messageData = "CREATE TABLE IF NOT EXISTS messageData (id INTEGER PRIMARY KEY AUTOINCREMENT, senderUPI TEXT, destinationUPI TEXT, time_stamp TEXT, message TEXT); "
	sql_create_table_profile = "CREATE TABLE IF NOT EXISTS userProfile (id INTEGER PRIMARY KEY AUTOINCREMENT, upi TEXT UNIQUE, fullname TEXT, position TEXT, description TEXT, location TEXT, picture TEXT); "
	conn = connectDatabase()
	c = conn.cursor()
	c.execute(sql_create_table_usersRegisters)
	c.execute(sql_create_table_messageData)
	c.execute(sql_create_table_profile)
	conn.commit()
	conn.close()
	pass

# Function that will take a connected database and add the registered users to the list
def addRegisteredUsers():
	dest = "http://cs302.pythonanywhere.com/listUsers"
	userList = urllib.urlopen(dest)
	list = tuple(userList.read().split(","))
	for user in list:
		addUser(user)
	pass

# Function will add single users one at a time to the database
def addUser(user):
	sql_insert_upi = 'INSERT OR IGNORE INTO userRegister(upi) VALUES(?) '
	conn = connectDatabase()
	c = conn.cursor()
	c.execute(sql_insert_upi, (user,))
	conn.commit()
	conn.close()
	pass

# Refresh Database will refresh and add the the activity of existing users in the list
def refreshDatabase(onlineUsers):
	dic = json.loads(onlineUsers)
	conn = connectDatabase()
	c = conn.cursor()
	for items in dic:
		try:
			sql_update_user = 'UPDATE userRegister SET ip==:ip, location==:location, last_login==:lastLogin, port==:port WHERE upi==:username'
			c.execute(sql_update_user, {"ip":dic[items]['ip'], "location":dic[items]['location'], "lastLogin":dic[items]['lastLogin'], "username":dic[items]['username'], "port":dic[items]['port']})
			try:
				sql_update_pubkey = 'UPDATE userRegister SET public_key==:publickey WHERE upi==:username'
				c.execute(sql_update_user, {"username":dic[items]['username'], "publickey":dic[items]['pubkey']})
			except Error as e:
				print e
		except KeyError as e:
			print e
		conn.commit()
	conn.close()
	return dic

def pingRefresh(sender):
	conn = connectDatabase()
	c = conn.cursor()
	epochtime = float(time.time())
	try:
		sql_update_user = 'UPDATE userRegister SET time_stamp==:time WHERE upi==:username'
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
				sql_insert_message = 'INSERT INTO messageData (senderUPI, time_stamp, message, destinationUPI) VALUES (:username, :time_stamp, :message, :destination)'
				c.execute(sql_insert_message, {"username":messageData['sender'], "time_stamp":messageData['stamp'], "message":messageData['message'], "destination":messageData['destination']})
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
		return 0

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
			sql_update_profile = 'UPDATE userProfile SET fullname = :fullname, ' \
			                     'position = :pos, ' \
			                     'description = :desc, ' \
			                     'location = :loc, ' \
			                     'picture = :pic WHERE upi==:upi'
			c.execute(sql_update_profile, {"upi": upi, "fullname": profileData['fullname'], "pos": profileData['position'],
		                               "desc": profileData['description'], "loc": profileData['location'],
		                               "pic": profileData['picture']})
			conn.commit()
			conn.close()
		except Error as e:
			print e
			return 1
	return 0

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
		return 0


# Connect to the database, returns the connection object
def connectDatabase():
	try:
		conn = sqlite3.connect("database.db")
	except Error as e:
		return e
	return conn
