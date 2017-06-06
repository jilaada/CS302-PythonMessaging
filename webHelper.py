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

#This function will be used to import designs in to the home page
def createHomePage(user):
	f = open("public/home.html")
	Page = f.read()
	f.close()
	# Get data from the database about the user
	profileData = databaseFunctions.getProfile(user)

	replaceText = '''<ul class="side-nav">
				<li style="width:100%"><a class="active" href="/">Home</a></li>
				<li style="width:100%"><a class="side" href="/messageWrite">Messages</a></li>
				<li style="width:100%"><a class="side" href="/editProfile">Edit Profile</a></li>
				<li style="width:100%"><a class="side" href="/">Settings</a></li>
				</ul>'''

	replaceText1 =   '''<div class="profile">
					<h2>
					''' + profileData['fullname'] + '''
					</h2>
					<div class="imgcontainer">
						<img src="''' + profileData['picture'] + '''" alt="Avatar" class="avatar">
					</div>
					<h3>
						Position: ''' + profileData['position'] + '''
					</h3>
					<h3>
						Location: ''' + profileData['location'] + '''
					</h3>
					<h3>
						Description: ''' + profileData['description'] + '''
					</h3>
					</div>'''

	Page = Page.replace('{:navActive}', replaceText)
	returnPage = Page.replace('{:profile}', replaceText1)
	return returnPage

def createEditProfile(user):
	f = open("public/home.html")
	Page = f.read()
	f.close()
	profileData = databaseFunctions.getProfile(user)

	replaceText = '''<ul class="side-nav">
					<li style="width:100%"><a class="side" href="/">Home</a></li>
					<li style="width:100%"><a class="side" href="/messageWrite">Messages</a></li>
					<li style="width:100%"><a class="active" href="/editProfile">Edit Profile</a></li>
					<li style="width:100%"><a class="side" href="/">Settings</a></li>
					</ul>'''

	replaceText1 = '''<div class="profile">
					<form action="/saveProfile" method="post" enctype="multipart/form-data" class="editProfile">
		            Name: <input type="text" name="fullname" value="''' + profileData['fullname'] + '''"/><br/>
                    Picture: <input type="text" name="picture" value="''' + profileData['picture'] + '''"/><br/>
		            Location: <input type="text" name="location" value="''' + profileData['location'] + '''"/><br/>
		            Position: <input type="text" name="position" value="''' + profileData['position'] + '''"/><br/>
		            Description:<br/> <textarea name="description">''' + profileData['description'] + '''</textarea><br/>
		            <button type="submit">Save Profile</button></form>
		            </div>'''

	Page = Page.replace('{:navActive}', replaceText)
	returnPage = Page.replace('{:profile}', replaceText1)
	return returnPage

def createMessages(user):
	f = open("public/home.html")
	Page = f.read()
	f.close()
	# Get the full list of users
	try:
		userList = externalComm.getAllUsers()
		list = tuple(userList.read().split(","))
	except Error as e:
		print e

	replaceText = '<ul class="side-nav">' \
	              '<li style="width:100% float:center"><a class="active" href="/">Home</a></li>'

	try:
		for user in list:
			replaceText += '<li style="width:100%"><a class="side" href="/">' + user + '</a></li>'
	except Error as e:
		print e

	replaceText1 = '<div class="messages"></div>'

	Page = Page.replace('{:navActive}', replaceText)
	returnPage = Page.replace('{:profile}', replaceText1)
	return returnPage