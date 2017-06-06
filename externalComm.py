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

import urllib
import urllib2
import json
import socket
import databaseFunctions
from sqlite3 import Error
import time

toggleThread = False

# External report tied to the thread
def externReport(curUser, curPw, curLocation):
	while toggleThread:
		# Need to try and report information to the login server as well as update the table list
		# Need to confirm thaat the user is logged in
		# If the username and the password as not none then they are logged in
		# do something
		try:
			error = autoReport(curUser, curPw, curLocation)
			usersOnline(curUser, curPw)
			print "ONLINE - " + curUser
		except Error as e:
			print e
			print "Something went wrong here"
		print "REPORTING"
		time.sleep(25)
	print "----------------------------"
	print "THREAD ENDING --- SIGNED OUT"
	print "----------------------------"


# Toggle whether or not the function thread should report the credentials
def toggleAuthority(setToggle):
	global toggleThread
	if setToggle is True:
		toggleThread = True
	else:
		toggleThread = False


# Report automatically to the server
def autoReport(username, password, curLocation):
	if curLocation == "0":
		# Get internal IP
		dataip = socket.gethostbyname(socket.gethostname())
	else:
		# Get external IP
		data = json.loads(urllib.urlopen("http://ip.jsontest.com/").read())
		dataip = data['ip']
	data = urllib2.urlopen('http://cs302.pythonanywhere.com/report?username=' + username + '&password=' + password + '&location=' + curLocation + '&ip=' + dataip + '&port=10001', timeout=10)
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
		data = urllib2.urlopen('http://cs302.pythonanywhere.com/getList?username=' + user + '&password=' + pw + '&enc=0&json=1', timeout=10)
	return data


# Function that will get the complete list of users
def getAllUsers():
	try:
		dest = "http://cs302.pythonanywhere.com/listUsers"
		userList = urllib.urlopen(dest)
	except Error as e:
		print e
	return userList


# Get the users who are online
def usersOnline(user, pw):
	users = autoGetList(user, pw).read()
	databaseFunctions.refreshDatabase(users)


# Send the message data to the users
def send(jsonDump, ip, port):
	dest = "http://" + ip + ":" + port + "/receiveMessage"
	try:
		req = urllib2.Request(dest, jsonDump, {'Content-Type':'application/json'})
		response = urllib2.urlopen(req, timeout=10)
	except urllib2.HTTPError, e:
		print e
		response = 0
	except urllib2.URLError, e:
		response = 0
	return response


# Send the message data to the users
def sendFile(jsonDump, ip, port):
	dest = "http://" + ip + ":" + port + "/receiveFile"
	try:
		req = urllib2.Request(dest, jsonDump, {'Content-Type':'application/json'})
		response = urllib2.urlopen(req, timeout=10)
	except urllib2.HTTPError, e:
		print e
		response = 0
	except urllib2.URLError, e:
		print e
		response = 0
	return response


# Send a requestion x address getting their profile
def reqProfile(jsonDump, ip, port):
	dest = "http://" + ip + ":" + port + "/getProfile?"
	try:
		req = urllib2.Request(dest, jsonDump, {'Content-Type':'application/json'})
		response = urllib2.urlopen(req, timeout=10)
		return response
	except urllib2.HTTPError, e:
		print e
	except urllib2.URLError, e:
		print e
	except Error as e:
		print e
	return 0
