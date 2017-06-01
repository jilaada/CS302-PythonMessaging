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
			Page += "Hello " + cherrypy.session['username'] + "!<br/>"
			Page += "Here is some bonus text because you've logged in!"
			Page += '<form action="/usersOnline" method="post" enctype="multipart/form-data">'
			Page += '<input type="submit" value="Get Users"/></form>'
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
		
		print threading.__file__
		return Page


	# The main web page for the website. The user is directed here when they first open the browser
	@cherrypy.expose
	def usersOnline(self):
		users = externalComm.getList(cherrypy.session.get('username'), cherrypy.session.get('password')).read()
		databaseFunctions.refreshDatabase(users)
		Page = users
		return Page



	#The login page for the server
	@cherrypy.expose
	def login(self):
		Page = '<form action="/signin" method="post" enctype="multipart/form-data">'
		Page += 'Username: <input type="text" name="username"/><br/>'
		Page += 'Password: <input type="password" name="password"/>'
		Page += '<input type="submit" value="Login"/></form>'
		return Page




	# LOGGING IN AND OUT
	@cherrypy.expose
	def signin(self, username=None, password=None):
		"""Check their name and password and send them either to the main page, or back to the main login screen."""
		error = self.authoriseUserLogin(username,password)
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

	# =================
	# Private functions  
	# =================

	def authoriseUserLogin(self, username, password):
		# Get hash of password
		hashpw = hashlib.sha256(password + "COMPSYS302-2017").hexdigest()
		ipadd = cherrypy.request.remote.ip
		dataip = json.loads(urllib.urlopen("http://ip.jsontest.com/").read())
		data = urllib.urlopen('http://cs302.pythonanywhere.com/report?username=' + username + '&password=' + hashpw + '&location=0&ip=' + '10.103.137.71' + '&port=10001')
		if data.read() == "0, User and IP logged":
			cherrypy.session['password'] = hashpw
			cherrypy.session['username'] = username
			t = threading.Thread(target=externalComm.externReport, args=(cherrypy.session['username'], cherrypy.session['password'],))
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
