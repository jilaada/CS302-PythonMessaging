#!/usr/bin/python
""" cherrypy_example.py

	COMPSYS302 - Software Design
	Author: Jilada Eccleston
	Last Edited: 4/05/2015

	This program uses the CherryPy web server (from www.cherrypy.org).
"""
# Requires:  CherryPy 3.2.2  (www.cherrypy.org)
#            Python  (We use 2.7)

import cherrypy
import json
import base64
import databaseFunctions
import externalComm
from sqlite3 import Error

# Function that will get the profile of a specific user
def profile(user):
	user_dict = {"profile_username": user}
	sendData = json.dumps(user_dict)
	data = databaseFunctions.getIP(user)
	try:
		sent = externalComm.reqProfile(sendData, data["ip"], data["port"])
		try:
			# Store values in the database
			databaseFunctions.storeProfile(sent.read(), user)
		except Error as e:
			print e
	except KeyError as e:
		print e
	return 0

# Function that will get the file and save it in directory
def saveFile(jsonDump):
	try:
		f = open("web/downloads/"+jsonDump['filename'], "w")
		data = base64.decodestring(jsonDump['file'])
		f.write(data)
		f.close()
		try:
			print "here"
		except Error as e:
			print "Error - " + e
	except (KeyError, TypeError) as e:
		print "Error - " + e
		return 1
	return 0
