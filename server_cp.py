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
from cherrypy.lib import static
import urllib
import hashlib
import sys
import json
import sqlite3
import threading
import time
import os
import os.path
import base64
import databaseFunctions
import externalComm
import internalComm
from sqlite3 import Error

# Getting directory
localDir = os.path.dirname(__file__)
absDir = os.path.join(os.getcwd(), localDir)

# The address we listen for connections on
listen_ip = "0.0.0.0"
try:
	listen_port = int(sys.argv[1])
except (IndexError, TypeError):
	listen_port = 10001

class MainApp(object):
	# CherryPy Configuration - uses a CherryPy config dictionary
	_cp_config = {'tools.encode.on': True,
				  'tools.encode.encoding': 'utf-8',
				  'tools.sessions.on': 'True',
				  'tools.staticdir.dir': os.path.abspath(os.getcwd()),
				 }

	# Function will be called when the user decides to go someone unspecified by the system
	@cherrypy.expose
	def default(self, *args, **kwargs):
		"""The default page, given when we don't recognise where the request is for."""
		Page = "I don't know where you're trying to go, so have a 404 Error."
		cherrypy.response.status = 404
		return Page


	# The main web page for the website. The user is directed here when they first open the browser
	@cherrypy.expose
	def index(self):
		Page = "Welcome! This is a test website for COMPSYS302!<br/>"
		try:
			users = databaseFunctions.dropdownGet()
			Page += "Hello " + cherrypy.session['username'] + "!<br/>"
			Page += "Here is some bonus text because you've logged in!"
			Page += '<form action="/usersOnline" method="post" enctype="multipart/form-data">'
			Page += '<input type="submit" value="Get Users"/></form>'
			Page += '<form action="/messageWrite" method="post" enctype="multipart/form-data">'
			Page += '<input type="submit" value="Send a Message"/></form>'
			Page += '<form action="/openFile" method="post" enctype="multipart/form-data">'
			Page += '<input type="submit" value="Send a File"/></form>'
			Page += '<form action="/myProfile" method="post" enctype="multipart/form-data">'
			Page += '<input type="submit" value="My Profile"/></form>'
			Page += '<form action="/userProfile" method="post" enctype="multipart/form-data">'
			Page += 'User: '
			Page += '<select name="user" id="customDropdown">'
			for i in users:
				Page += '<option value=' + i + '>' + i + '</option>'
			Page += '</select>'
			Page += '<input type="submit" value="Get Profile"/></form>'
		except (KeyError, TypeError): #There is no username
			Page += "Click here to <a href='login'>login</a>."
		# Upon trying to connect to the home page, the server will try to connect to a database
		# if the database does not exist it will make it and close it
		try:
			conn = sqlite3.connect("database.db")
		except Error as e:
			print(e)
		finally:
			conn.close()
			cherrypy.session['database'] = "on"

		# This section determines if there is a database
		if cherrypy.session['database'] is not None:
			databaseFunctions.createTable()
			databaseFunctions.addRegisteredUsers()

		return Page


	# The main web page for the website. The user is directed here when they first open the browser
	@cherrypy.expose
	def usersOnline(self):
		users = databaseFunctions.dropdownGet()
		Page = "Here is a list of all the users online!<br/><br/>"
		for i in users:
			Page += i + '<br/>'
		return Page


	#The login page for the server
	@cherrypy.expose
	def login(self):
		Page = '<form action="/signin" method="post" enctype="multipart/form-data">'
		Page += 'Username: <input type="text" name="username"/><br/>'
		Page += 'Password: <input type="password" name="password"/><br/>'
		Page += 'Location: '
		Page += '<select name="location" id="customDropdown">'
		Page += '<option value=0>Uni Remote Linux</option><br/>'
		Page += '<option value=1>Uni Wi-Fi</option><br/>'
		Page += '<option value=2>External IP</option><br/>'
		Page += '</select><br/>'
		Page += '<input type="submit" value="Login"/></form>'
		return Page


	# LOGGING IN AND OUT
	@cherrypy.expose
	def signin(self, username=None, password=None, location=None):
		"""Check their name and password and send them either to the main page, or back to the main login screen."""
		error = self.authoriseUserLogin(username, password, location)
		if error == 0:
			raise cherrypy.HTTPRedirect('/')
		else:
			raise cherrypy.HTTPRedirect('/login')


	@cherrypy.expose
	def signout(self):
		"""Logs the current user out, expires their session"""
		username = cherrypy.session.get('username')
		password = cherrypy.session.get('password')
		if username is None:
			pass
		else:
			data = urllib.urlopen('http://cs302.pythonanywhere.com/logoff?username=' + username + '&password=' + password + '&enc=0')
			externalComm.toggleAuthority(False)
			print data.read()
			cherrypy.lib.sessions.expire()
			cherrypy.session['username'] = None
			cherrypy.session['password'] = None
			cherrypy.session['location'] = None
		raise cherrypy.HTTPRedirect('/')


	@cherrypy.expose
	@cherrypy.tools.json_in()
	def receiveMessage(self):
		inputMessage = cherrypy.request.json
		databaseFunctions.insertMessage(inputMessage)
		print inputMessage
		return "0"


	@cherrypy.expose
	def messageWrite(self):
		users = databaseFunctions.dropdownGet()
		Page = '<form action="/sendMessage" method="post" enctype="multipart/form-data">'
		Page += 'Receiver: '
		Page += '<div>'
		Page += '<select name="destination" id="customDropdown">'
		for i in users:
			Page += '<option value=' + i + '>' + i + '</option>'
		Page += '</select>'
		Page += '</div>'
		Page += 'Message: <input type="text" name="message"/>'
		Page += '<input type="submit" value="Send"/></form>'
		return Page


	@cherrypy.expose
	@cherrypy.tools.json_in()
	def receiveFile(self):
		inputFile = cherrypy.request.json
		internalComm.saveFile(inputFile)
		print inputFile
		return "0"


	@cherrypy.expose
	def openFile(self):
		users = databaseFunctions.dropdownGet()
		Page = '<form action="/sendFile" method="post" enctype="multipart/form-data">'
		Page += 'Receiver: '
		Page += '<div>'
		Page += '<select name="destination" id="customDropdown">'
		for i in users:
			Page += '<option value=' + i + '>' + i + '</option>'
		Page += '</select>'
		Page += '</div>'
		Page += 'Specify a file: </br>'
		Page += '<input type="file" name="dataFile"/></br>'
		Page += '<input type="submit" value="Send"/></form>'
		return Page


	# leave this until Hamish
	@cherrypy.expose
	def sendFile(self, destination=None, dataFile=None):
		sender = cherrypy.session['username']
		epoch_time = float(time.time())
		hashing = int(0)
		size = 0
		try:
			data = dataFile.file.read()
			base64data = base64.encodestring(data)
			output_dict = {"sender":sender, "destination":destination, "file":base64data, "filename":(dataFile.filename), "content_type":str(dataFile.content_type), "stamp":epoch_time, "hashing":hashing}
			out_json = json.dumps(output_dict)
			try:
				ipdata = databaseFunctions.getIP(destination)
				send = externalComm.sendFile(out_json, ipdata["ip"], ipdata["port"])
			except Error as e:
				print e
		except Error as e:
			print e
		pass


	@cherrypy.expose
	@cherrypy.tools.json_in()
	def getProfile(self):
		inputMessage = cherrypy.request.json
		user = inputMessage["profile_username"]
		if user == "jecc724":
			profileData = databaseFunctions.getProfile(user)
			encoding = int(2)
			encryption = int(0)
			output_dict = {"fullname":profileData['fullname'], "position":profileData['position'], "description":profileData['description'],
			               "location":profileData['location'], "picture":profileData['picture'], "encoding":encoding, "encryption":encryption}
			return json.dumps(output_dict)
		pass


	@cherrypy.expose()
	def myProfile(self):
		# Fetch values from database
		profileData = databaseFunctions.getProfile(cherrypy.session['username'])
		Page = 'This page will display data about the user</br></br>'
		Page += 'Name : ' + profileData['fullname'] + '</br>'
		Page += 'Profile Picture : </br>'
		Page += '<img src="' + profileData['picture'] + '" alt="Doggo"></br>'
		Page += 'Location : ' + profileData['location'] + '</br>'
		Page += 'Position : ' + profileData['position'] + '</br>'
		Page += 'Description : ' + profileData['description'] + '</br>'
		Page += '<form action="/editProfile" method="post" enctype="multipart/form-data">'
		Page += '<input type="submit" value="Edit Profile"/></form>'
		return Page


	@cherrypy.expose()
	def editProfile(self):
		profileData = databaseFunctions.getProfile(cherrypy.session['username'])
		Page = 'This page will display data about the user</br></br>'
		Page += '<form action="/saveProfile" method="post" enctype="multipart/form-data">'
		Page += 'Name: <input type="text" name="fullname" value="' + profileData['fullname'] + '"/><br/>'
		Page += 'Location: <input type="text" name="location" value="' + profileData['location'] + '"/><br/>'
		Page += 'Position: <input type="text" name="position" value="' + profileData['position'] + '"/><br/>'
		Page += 'Description: <input type="text" name="description" value="' + profileData['description'] + '"/><br/>'
		Page += 'Picture: <input type="text" name="picture" value="' + profileData['picture'] + '"/><br/>'
		Page += '<input type="submit" value="Save Profile"/></form>'
		return Page


	@cherrypy.expose
	def sendMessage(self, destination=None, message=None):
		epoch_time = float(time.time())
		output_dict = {"sender":"jecc724", "destination":destination, "message":message, "stamp":epoch_time, "encoding":2}
		ins = databaseFunctions.insertMessage(output_dict)
		if ins == 1:
			print "Error - Message did not store properly"
		sendData = json.dumps(output_dict)
		try:
			data = databaseFunctions.getIP(destination)
			if data["ip"] is None or data["port"] is None:
				print "Error - Unable to send the user the message, they don't exist on the database!"
			else:
				try:
					sent = externalComm.send(sendData, data["ip"], data["port"])
					print sent
				except KeyError:
					raise cherrypy.HTTPRedirect('/')
		except (KeyError, TypeError) as e:
			print e
		raise cherrypy.HTTPRedirect('/messageWrite')


	@cherrypy.expose()
	def userProfile(self, user=None):
		try:
			internalComm.profile(user)
			raise cherrypy.HTTPRedirect('/')
		except (KeyError, TypeError):
			raise cherrypy.HTTPRedirect('/')


	@cherrypy.expose()
	def saveProfile(self, fullname=None, location=None, position=None, description=None, picture=None):
		output_dict = {"fullname": fullname, "position": position, "description": description, "location": location, "picture": picture}
		json_dump = json.dumps(output_dict)
		try:
			databaseFunctions.storeProfile(json_dump, cherrypy.session['username'])
		except Error as e:
			print e
		raise cherrypy.HTTPRedirect('/myProfile')

	# =================
	# Other functions
	# =================

	@cherrypy.expose()
	def listAPI(self):
		output_dict = "/<receiveMessage>[sender][destination][message][stamp]/<getProfile>[profile_username]/<ping>[sender]Encoding/<receiveFile>[sender][destination][file]<2>Encryption<0>Hashing<0>"
		return output_dict


	@cherrypy.expose()
	def ping(self, sender):
		databaseFunctions.pingRefresh(sender)
		return 0


	@cherrypy.expose
	@cherrypy.tools.json_in()
	def handshake(self):
		inputMessage = cherrypy.request.json
		pass

	# =================
	# Private functions
	# =================

	def authoriseUserLogin(self, username, password, location):
		# Get hash of password
		hashpw = hashlib.sha256(password + "COMPSYS302-2017").hexdigest()
		try:
			error = externalComm.autoReport(username, hashpw, location)
		except (KeyError, TypeError) as e:
			print e
			raise cherrypy.HTTPRedirect('/login')
		if error == 0:
			cherrypy.session['password'] = hashpw
			cherrypy.session['username'] = username
			print cherrypy.session['username']
			cherrypy.session['location'] = location
			t = threading.Thread(target=externalComm.externReport, args=(cherrypy.session['username'], cherrypy.session['password'], cherrypy.session['location']))
			t.daemon = True
			externalComm.toggleAuthority(True)
			t.start()
			print "-----------------------"
			print "--- THREAD STARTING ---"
			print "-----------------------"
			return 0
		else:
			cherrypy.session['password'] = None
			cherrypy.session['username'] = None
			cherrypy.session['location'] = None
			return 1



def runMainApp():
	# Create an instance of MainApp and tell Cherrypy to send all requests under / to it. (ie all of them)
	cherrypy.tree.mount(MainApp(), "/")

	# Tell Cherrypy to listen for connections on the configured address and port.
	cherrypy.config.update({'server.socket_host': listen_ip,
							'server.socket_port': listen_port,
							'engine.autoreload.on': True,
						   })

	print "========================================"
	print "University of Auckland"
	print "COMPSYS302 - Software Design Application"
	print "Jilada Eccleston"
	print "========================================"

	# Start the web server
	cherrypy.engine.start()

	# And stop doing anything else. Let the web server take over.
	cherrypy.engine.block()

#Run the function to start everything
if __name__ == '__main__':
	runMainApp()
