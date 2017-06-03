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


import cherrypy
import urllib
import urllib2
import hashlib
import sys
import json
import threading
import sqlite3
from sqlite3 import Error

# =====================
# Database Manipulation
# =====================

# Function that will take a connected database and add the table headers
def createTable():
	sql_create_table_usersRegisters = "CREATE TABLE IF NOT EXISTS userRegister (id INTEGER PRIMARY KEY AUTOINCREMENT, upi TEXT UNIQUE, ip TEXT, public_key TEXT, location INTEGER, last_login TEXT, port TEXT); "
	sql_create_table_messageData = "CREATE TABLE IF NOT EXISTS messageData (id INTEGER PRIMARY KEY AUTOINCREMENT, senderUPI TEXT , time_stamp TEXT, message TEXT); "
	conn = connectDatabase()
	c = conn.cursor()
	c.execute(sql_create_table_usersRegisters)
	c.execute(sql_create_table_messageData)
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
		except KeyError as e:
			print e
		conn.commit()
	conn.close()
	return dic

# Refresh the message database so that messages are stored in teh database
def insertMessage(messageData):
	conn = connectDatabase()
	c = conn.cursor()
	try:
		# Assuming they are not 
		#sql_select_message = 'SELECT * FROM messageData WHERE senderUPI==:username AND time_stamp==:time_stamp'
		#c.execute(sql_select_message, {"username":messageData['sender'], "time_stamp":messageData['stamp']})
		#if c.fetchone() is None:
			#try:
		sql_insert_message = 'INSERT INTO messageData (senderUPI, time_stamp, message) VALUES (:username, :time_stamp, :message)'
		c.execute(sql_insert_message, {"username":messageData['sender'], "time_stamp":messageData['stamp'], "message":messageData['message']})
		conn.commit()
			#except Error as e:
				#print e
		#else:
			#print "Message saved already"
	except Error as e:
		print e
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


# Connect to the database, returns the connection object
def connectDatabase():
	try:
		conn = sqlite3.connect("database.db")
	except Error as e:
		return e
	return conn
