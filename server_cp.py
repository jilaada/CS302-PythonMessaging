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
import sqlite3
import threading
import time
import socket
import databaseFunctions
import externalComm
from sqlite3 import Error

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
			Page += '<form action="/profile" method="post" enctype="multipart/form-data">'
			Page += 'User: '
			Page += '<select name="user" id="customDropdown">'
			for i in users:
				Page += '<option value=' + i + '>' + i + '</option>'
			Page += '</select>'
			Page += '<input type="submit" value="Get Profile"/></form>'
		except KeyError: #There is no username
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
		print location
		error = self.authoriseUserLogin(username,password, location)
		if error == 0:
			Page = "Welcome! This is a test website for COMPSYS302! You have logged in!<br/>"
			return Page
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
		raise cherrypy.HTTPRedirect('/')


	@cherrypy.expose
	@cherrypy.tools.json_in()
	def receiveMessage(self):
		inputMessage = cherrypy.request.json
		# Need some way of taking this message and saving it in the database
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
	def getProfile(self):
		inputMessage = cherrypy.request.json
		username = inputMessage["profile_username"]
		if username == "jecc724":
			fullname = "Jilada Eccleston"
			position = "Occupational Student"
			description = "I'm at risk of failing this course"
			location = "Upstairs Lab"
			picture = "https://pbs.twimg.com/media/CdrOk7LWoAEdT6P.jpg"
			encoding = int(2)
			encryption = int(0)
			output_dict = {"fullname":fullname, "position":position, "description":description, "location":location, "picture":picture, "encoding":encoding, "encryption":encryption}
			#sendData = json.dumps(output_dict)
			return json.dumps(output_dict)
		pass


	@cherrypy.expose
	def profile(self, user=None):
		user_dict = {"profile_username":user}
		sendData = json.dumps(user_dict)
		# Need to get the port and ip of the user
		data = databaseFunctions.getIP(user)
		try:
			sent = externalComm.reqProfile(sendData, data["ip"], data["port"])
			try:
				# Store values in the database
				databaseFunctions.storeProfile(sent.read(), user)
				#print sent.read()
			except Error as e:
				print e
				print "Profile doesn't exist probably"
		except Error as e:
			print e
		raise cherrypy.HTTPRedirect('/')


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
					try:
						print sent.read()
					except Error as e:
						print e
				except Error as e:
					raise cherrypy.HTTPRedirect('/')
		except Error as e:
			print e 
		raise cherrypy.HTTPRedirect('/messageWrite')

	# =================
	# Private functions  
	# =================

	def authoriseUserLogin(self, username, password, location):
		# Get hash of password
		hashpw = hashlib.sha256(password + "COMPSYS302-2017").hexdigest()
		if location == "0":
			# Get internal IP
			dataip = socket.gethostbyname(socket.gethostname())
		else:
			# Get external IP 
			ipadd = cherrypy.request.remote.ip
			dataip = json.loads(urllib.urlopen("http://ip.jsontest.com/").read())
		try:
			data = urllib.urlopen('http://cs302.pythonanywhere.com/report?username=' + username + '&password=' + hashpw + '&location=' + location + '&ip=' + dataip + '&port=10001')
		except KeyError:
			raise cherrypy.HTTPRedirect('/login')
		if data.read() == "0, User and IP logged":
			cherrypy.session['password'] = hashpw
			cherrypy.session['username'] = username
			cherrypy.session['location'] = location
			t = threading.Thread(target=externalComm.externReport, args=(cherrypy.session['username'], cherrypy.session['password'], cherrypy.session['location']))
			cherrypy.session['threadOne'] = t
			t.daemon = True
			externalComm.toggleAuthority(True)
			t.start()
			return 0
		else:
			cherrypy.session['password'] = None
			cherrypy.session['username'] = None
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
