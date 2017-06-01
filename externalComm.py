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
# Used for threading the report and the update of user lists

import cherrypy
import urllib
import urllib2
import hashlib
import sys
import json
import sqlite3
import threading
import databaseFunctions
from sqlite3 import Error
import time

toggleThread = False

def externReport(curUser, curPw):
	while(1):
		# Need to try and report information to the login server as well as update the table list
		# Need to confirm thaat the user is logged in
		# If the username and the password as not none then they are logged in
		if toggleThread:
			# do something
			try:
				error = autoReport(curUser, curPw)
				usersOnline(curUser, curPw)
				print "You are online - " + curUser
			except Error as e:
				print e
				print "Something went wrong here"
			print "Reporting"
		time.sleep(25)

def toggleAuthority(setToggle):
	global toggleThread
	if setToggle is True:
		toggleThread = True
	else:
		toggleThread = False

def autoReport(username, password):
	ipadd = cherrypy.request.remote.ip
	dataip = json.loads(urllib.urlopen("http://ip.jsontest.com/").read())
	data = urllib.urlopen('http://cs302.pythonanywhere.com/report?username=' + username + '&password=' + password + '&location=0&ip=' + '10.103.137.71' + '&port=10001')
	error = data.read()
	if error[0] is "0":
		return 0
	else:
		print error
		return 1

# Function that will allow the user to get a list of the current users online and display them in the terminal
def autoGetList(user, pw):
	# Check for a valid username
	if user is None:
		data = "You are not signed in"
	else:
		data = urllib.urlopen('http://cs302.pythonanywhere.com/getList?username=' + user + '&password=' + pw + '&enc=0&json=1')
		# Need another functions that will write and read from the database
	return data

def usersOnline(user, pw):
	users = autoGetList(user, pw).read()
	databaseFunctions.refreshDatabase(users)
