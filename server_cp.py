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
import webHelper
from sqlite3 import Error

# Getting directory
localDir = os.path.dirname(__file__)
absDir = os.path.join(os.getcwd(), localDir)
activeUser = ""

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
				  'tools.sessions.on': True,
				  'tools.staticdir.on': True,
				  'tools.staticdir.dir': os.path.abspath(os.getcwd()),
				 }


	# ==================================================================
	# CherryPy Server Functions
	# ==================================================================

	def __init__(self):
		cherrypy.engine.subscribe('stop',self.shutdownActions)

	def shutdownActions(self):
		'''
		This function will allow the application signout all users in the database that are logged in
		'''
		print "----------------------------------"
		print "ENGINE SHUTTING OFF - AUTO LOG-OFF"
		print "----------------------------------"
		data = databaseFunctions.getLogged()
		for item in data:
			data = urllib.urlopen('http://cs302.pythonanywhere.com/logoff?username=' + item[0] + '&password=' + item[1] + '&enc=0')
			print data.read()
		print "----------------------------------"
		print "SHUT DOWN COMPLETE"
		print "----------------------------------"


	# ==================================================================
	# Webpage Nav Functions
	# ==================================================================

	@cherrypy.expose
	def default(self, *args, **kwargs):
		'''
		Default function call if an address does not exist
		'''
		Page = "The page you are requesting does not exist: <a href='/' >click here</a>"
		cherrypy.response.status = 404
		return Page


	@cherrypy.expose
	def index(self):
		'''
		The main web page for the website. The user is directed here when they first open the browser
		
		:return redirect to a webpage
		'''
		# Try connect to the database if it doesn't exist
		# Create tables if they don't exist
		# Get all the users and add to register
		try:
			conn = sqlite3.connect("database.db")
		except Exception as e:
			print(e)
		finally:
			conn.close()
			cherrypy.session['database'] = "on"

		print "About to create tables"
		databaseFunctions.createTable()
		print "tables created"
		users = externalComm.getAllUsers()
		databaseFunctions.addRegisteredUsers(users)

		# Try to create a log in page using valid cherrypy sessions
		# Raise a key error or a type error and redirect to the login page if the session doesn't exist
		try:
			Page = webHelper.createHomePage(cherrypy.session['username'])
		except (KeyError, TypeError):
			raise cherrypy.HTTPRedirect('/login')
		return Page


	@cherrypy.expose
	def signin(self, username=None, password=None, location=None):
		'''
		Function that is called when the user submits the form for signing in
		
		:param username of the user
		:param password of the user
		:param location of the user
		:return redirect to a webpage
		'''
		# Check their name and password and send them either to the main page, or back to the main login screen
		error = self.authoriseUserLogin(username, password, location)
		if error == 0:
			raise cherrypy.HTTPRedirect('/')
		else:
			raise cherrypy.HTTPRedirect('/login')


	@cherrypy.expose
	def login(self):
		'''
		The main web page for the website. The user is directed here when they are authenticated
		Displays the navigation pane as well as their profile
		
		:return redirect to the main login for the webpage
		'''
		f = open("public/index.html")
		Page = f.read()
		f.close()
		return Page



	@cherrypy.expose
	def signout(self):
		'''
		Function to called when the user clicks to signout
		Removes all credentials from the session and reports the user as offline on the login server
		
		:return redirect to a the main log in page for the webpage
		'''
		# Log the current user out, expires their session when the user presses the log out button on the website
		print "-------------------------"
		print "SIGNING OUT OF THE SERVER"
		print "-------------------------"
		username = cherrypy.session.get('username')
		password = cherrypy.session.get('password')
		# Signout if credentials exist
		if username is None:
			pass
		else:
			data = urllib.urlopen('http://cs302.pythonanywhere.com/logoff?username=' + username + '&password=' + password + '&enc=0')
			print data.read()
			# Will toggle a release on the thread for reporting
			externalComm.toggleAuthority(False)
			# Change the user's status
			databaseFunctions.storeStatus(json.dumps({"status":"Offline"}), cherrypy.session['username'])
			# Expire all sessions
			cherrypy.lib.sessions.expire()
			cherrypy.session['username'] = None
			cherrypy.session['password'] = None
			cherrypy.session['location'] = None
		raise cherrypy.HTTPRedirect('/')


	@cherrypy.expose
	def messageWrite(self):
		'''
		Creates the message display and writing interface
		
		:return return the main page or the redirects to the login page
		'''
		try:
			# Uses sessions to verify user authentication
			Page = webHelper.createMessages(cherrypy.session['username'], cherrypy.session['password'])
		except KeyError as e:
			raise cherrypy.HTTPRedirect('/')
		return Page


	@cherrypy.expose()
	def editProfile(self):
		'''
		Creates the edit profile page
		
		:return return the main profile page or the redirects to the login page
		'''
		try:
			Page = webHelper.createEditProfile(cherrypy.session['username'])
		except KeyError as e:
			print "Error - no session"
			raise cherrypy.HTTPRedirect('/')
		return Page


	# ==================================================================
	# External Call Functions
	# ==================================================================


	@cherrypy.expose
	@cherrypy.tools.json_in()
	def receiveMessage(self):
		'''
		Called by the clients request to send this client a message
		should return an error code - how returns only "0"
		
		:param input message from the other client as a json object
		:return returns an error code deduced from the storing of the message
		'''
		inputMessage = cherrypy.request.json
		data = databaseFunctions.insertMessage(inputMessage)
		return data


	@cherrypy.expose
	@cherrypy.tools.json_in()
	def receiveFile(self):
		'''
		Called by the clients requesting that a file be sent to this client
		
		:param input file from the other client as a json object
		:return returns an error code deduced from the storing of the message
		'''
		inputFile = cherrypy.request.json
		internalComm.saveFile(inputFile)
		data = databaseFunctions.storeFile(inputFile)
		return data


	@cherrypy.expose
	@cherrypy.tools.json_in()
	def getProfile(self):
		'''
		Other users will call get profile to get user's profile data
		
		:param input file from the other client as a json object include the sender and the upi of the use they are after
		:return returns the profile of the user as a json object
		'''
		inputMessage = cherrypy.request.json
		try:
			user = inputMessage["profile_username"]
		except (KeyError, TypeError) as e:
			print str(e)
			return "1"
		profileData = databaseFunctions.getProfile(user)
		encryption = int(0)
		output_dict = {"fullname":profileData['fullname'], "position":profileData['position'], "description":profileData['description'], "location":profileData['location'], "picture":profileData['picture'], "encryption":encryption}
		return json.dumps(output_dict)


	@cherrypy.expose()
	def listAPI(self):
		'''
		Allows other users to see the available API calls for tjhis client
		
		:return returns a string with formatted list of apis available to use
		'''
		output_dict = 	"/<getStatus>[profile_username]\n/<acknowledgeEvent>[sender][event_name][attendance][start_time]\n" \
						"/<receiveMessage>[sender][destination][message][stamp]\n" \
						"/<getProfile>[profile_username]\n/<ping>[sender]\n" \
						"/<receiveFile>[sender][destination][file]\n" \
						"/<receiveEvents>[sender][destination][event_name][event_description][event_location][start_time][end_time]\n" \
						"Encryption 0\nHashing 0"
		return output_dict


	@cherrypy.expose()
	def ping(self, sender=None):
		'''
		Pings the user and reutrn a 0 string - update teh sever with the new user's current time
		
		:return returns "0"
		'''
		databaseFunctions.pingRefresh(sender)
		return "0"



	# ==================================================================
	# Internal to External Call Functions
	# ==================================================================

	@cherrypy.expose
	def sendFile(self, dataFile=None):
		'''
		Call send file to send a file to another client who is online
		
		:return returns the file to be sent to other users
		'''
		global activeUser
		sender = cherrypy.session['username']
		destination = activeUser
		epoch_time = float(time.time())
		hashing = int(0)
		size = 0
		try:
			# encode the data
			data = dataFile.file.read()
			base64data = base64.encodestring(data)
			output_dict = {"sender":sender, "destination":destination, "file":base64data, "filename":(dataFile.filename), "content_type":str(dataFile.content_type), "stamp":epoch_time, "hashing":hashing}
			out_json = json.dumps(output_dict)
			try:
				# Get the user parameters
				ipdata = databaseFunctions.getIP(destination)
				send = externalComm.sendFile(out_json, ipdata["ip"], ipdata["port"])
				databaseFunctions.storeFile(output_dict)
				try:
					# Store the file sent in the folder to be displayed on the screen
					internalComm.saveFile(output_dict)
				except Error as e:
					print e
				if send == "0":
					print "--- File Sent Successfully ---"
				else:
					print "--- File Sent Unsuccessful ---"
			except Error as e:
				print e
		except Error as e:
			print e
		pass



	# ==================================================================
	# Internal Call Functions
	# ==================================================================

	def sendText(self, message):
		'''
		This function is called to send a message to the clients
		
		:return returns the file to be sent to other users
		'''
		#Get sender parameters
		destination = activeUser
		epoch_time = float(time.time())
		output_dict = {"sender":cherrypy.session['username'], "destination":destination, "message":message, "stamp":epoch_time}
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
					if sent == 0:
						print "--- Message Sent Unsuccessful ---"
					else:
						print "--- Message Sent Successfully ---"
				except KeyError:
					raise cherrypy.HTTPRedirect('/')
		except (KeyError, TypeError) as e:
			print e
		return "0"



	# ==================================================================
	# Exposed for Web Functions
	# ==================================================================

	# Get the current user's profile from the database
	@cherrypy.expose()
	def userProfile(self, user):
		try:
			internalComm.profile(user, cherrypy.session['username'])
			try:
				data = databaseFunctions.getProfile(user)
				if data is None:
					output_dict = {"fullname":user, "position":"Not Specified", "description":"Not Specified", "location":"Not Specified", "picture":"https://sorted.org.nz/themes/sorted/assets/images/user-icon-grey.svg"}
				else:
					profile = [sub for sub in data]
					output_dict = {"fullname": profile[2], "position": profile[3], "description": profile[4], "location": profile[5], "picture": profile[6]}
				print output_dict
				return json.dumps(output_dict)
			except Error as e:
				print e
		except (KeyError, TypeError) as e:
			print str(e)
			print "Getting profile failed"


	# Allows for the profile form to be sibmitted and save from the website
	@cherrypy.expose()
	def saveProfile(self, fullname=None, location=None, position=None, description=None, picture=None):
		output_dict = {"fullname": fullname, "position": position, "description": description, "location": location, "picture": picture}
		json_dump = json.dumps(output_dict)
		try:
			databaseFunctions.storeProfile(json_dump, cherrypy.session['username'])
		except Error as e:
			print e
		raise cherrypy.HTTPRedirect('/')


	# Allows for the event form to be submitted form the the website
	@cherrypy.expose()
	def createEvent(self, guest=None, name=None, start=None, end=None, desc=None, loc=None):
		pattern = '%d-%m-%Y %H:%M:%S'
		try:
			start_epoch = float(time.mktime(time.strptime(start, pattern)))
			end_epoch = float(time.mktime(time.strptime(start, pattern)))
		except Error as e:
			print str(e)
			raise cherrypy.HTTPRedirect('/')
		#Try to send to user then add to 
		output_dict = {"sender":str(cherrypy.session['username']), "destination": guest, "event_name": name, "event_description": desc, "event_location": loc, "start_time": start_epoch, "end_time":end_epoch, "attendance": 0}
		dataIP = databaseFunctions.getIP(guest)
		result = externalComm.reqEvent(output_dict, dataIP['ip'], dataIP['port'])
		if result == 0:
		# Add to the database
			databaseFunctions.addEvent(output_dict, cherrypy.session['username'])
		else:
			print "Sending to guest unsuccessful"
		raise cherrypy.HTTPRedirect('/')


	# =================
	# Other functions
	# =================

	# Get the status of the user
	@cherrypy.expose()
	@cherrypy.tools.json_in()
	def getStatus(self):
		inputMessage = cherrypy.request.json
		status = databaseFunctions.getStatus(inputMessage['profile_username'])
		if status == "0":
			jsonDump = json.dumps({"status":"Offline"})
		else:
			jsonDump = json.dumps({"status":status})
		return jsonDump


	# Get messages to be displayed on the screen of the webpage
	@cherrypy.expose()
	def getMessages(self, user):
		messages = databaseFunctions.getMessages(user, cherrypy.session['username'])
		html = webHelper.createViewMessage(messages, cherrypy.session['username'])
		return html


	# Get the refreshed user list
	@cherrypy.expose()
	def refreshUserList(self):
		html = webHelper.createUserList(cherrypy.session['username'], cherrypy.session['password'])
		print "Refreshing Users"
		return html


	# Toggle the active user
	@cherrypy.expose()
	def toggleActiveUser(self, user):
		global activeUser
		activeUser = user

	# send teh messages to the user - call from the webservice
	@cherrypy.expose()
	def sendMessage(self, message):
		self.sendText(message)
		return "0"

	# Get thte profile of the user for the webpage
	@cherrypy.expose()
	def getUserProfile(self):
		try: 
			data = databaseFunctions.getProfile(cherrypy.session['username'])
			if data is not None:
				profile = [sub for sub in data]
				output_dict = {"fullname": profile[2], "position": profile[3], "description": profile[4], "location": profile[5], "picture": profile[6]}
			else:
				output_dict = {"fullname": cherrypy.session['username'], "position": "Not Specified", "description": "Not Specified",
				               "location": "Not Specified",
				               "picture": "https://sorted.org.nz/themes/sorted/assets/images/user-icon-grey.svg"}
			return json.dumps(output_dict)
		except Error as e:
			print e
			return "1, profile not found" 

	# Get all the users in the list
	@cherrypy.expose()
	def getAllUsers(self):
		userList = databaseFunctions.getUsers()
		dic = {}
		for index, item in enumerate(userList):
			dic[index] = {"upi": item[0]}
		return json.dumps(dic)


	# Store the status of the users
	@cherrypy.expose()
	def storeStatus(self, status):
		# Save the status in the database
		dic = {"status":status}
		jsonDump = json.dumps(dic)
		databaseFunctions.storeStatus(jsonDump, cherrypy.session['username'])


	# Recevie events from other users
	@cherrypy.expose()
	@cherrypy.tools.json_in()
	def receiveEvent(self):
		inputMessage = cherrypy.request.json
		print inputMessage
		try:
			output_dict = {"guest":inputMessage['destination'], "event_name":inputMessage['event_name'], "event_desc":inputMessage['event_description'], "event_loc":inputMessage['event_location'], "start_time":inputMessage['start_time'], "end_time":inputMessage['end_time'], "attendance": 0}
			databaseFunctions.addEvent(output_dict, inputMessage['sender'])
			print "Here right now"
		except KeyError as e:
			print str(e)
			try:
				output_dict = {"guest": inputMessage['destination'], "event_name": inputMessage['event_name'], "start_time": inputMessage['start_time'], "end_time": inputMessage['end_time'], "attendance": 0}
				databaseFunctions.addEvent(output_dict, inputMessage['sender'])
			except KeyError as e:
				print str(e)
				return "1"
		return "0"


	# Acknowledge the event from otehr users
	@cherrypy.expose()
	@cherrypy.tools.json_in()
	def acknowledgeEvent(self):
		inputAcknowledge = cherrypy.request.json
		update = databaseFunctions.updateEvent(inputAcknowledge)
		if update == 0:
			print "Event is updated"
		else:
			print "Event has been successfully updated"
		return "0"


	# get the events to be displayed on the screen
	@cherrypy.expose()
	def getEvents(self, toggle):
		# Get the events from the database
		if toggle == "0":
			eventList = databaseFunctions.gatherEvents(cherrypy.session['username'], 0)
		else:
			eventList = databaseFunctions.gatherEvents(cherrypy.session['username'], 1)
		if eventList is not 1:
			dic = []
			for item in eventList:
				end_time = time.strftime('%d-%m-%Y %H:%M:%S', time.localtime(float(item[6])))
				start_time = time.strftime('%d-%m-%Y %H:%M:%S', time.localtime(float(item[5])))
				dic.append({"host": item[2], "guest": item[3], "event_name": item[4], "description": item[8], "location": item[9], "end_time": end_time, "start_time": start_time, "id":item[0], "attendance":item[7]})
		else:
			dic = {"Event":"None"}
		return json.dumps(dic)


	# acknowledge the host - an external call from the website
	@cherrypy.expose()
	def acknowledgeHost(self, attendance, row_id):
		# Update the attendance
		try:
			host = databaseFunctions.updateAttendance(attendance, row_id)
			dataIP = databaseFunctions.getIP(host[0])
			jsonDump = {"sender":cherrypy.session['username'], "event_name":host[1], "attendance":attendance, "start_time":host[2]}
			result = externalComm.reqAcknowledge(jsonDump, dataIP['ip'], dataIP['port'])
			if result == 0:
				print "--- Acknowledgement sent ---"
			else:
				print result
		except Exception as e:
			print str(e)
			print "Acknowledgement did not send properly"

	# =================
	# Private functions
	# =================


	# Authorise the user logins credentials
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
			cherrypy.session['location'] = location
			databaseFunctions.updateLogged(username, hashpw)
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
	conf = {
		'/': {
			'tools.sessions.on': True,
			'tools.staticdir.root': os.path.abspath(os.getcwd())
		},
		'/static': {
			'tools.staticdir.on': True,
			'tools.staticdir.dir': './public'
		}
	}
	
	runMainApp()
