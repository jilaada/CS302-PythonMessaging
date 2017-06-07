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
    
	script = "<script></script>"
	Page = Page.replace('{:navActive}', replaceText)
	Page = Page.replace('{:script}', script)
	returnPage = Page.replace('{:profile}', replaceText1)
	return returnPage


# Edit main profile page
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
    
	script = "<script></script>"
	Page = Page.replace('{:navActive}', replaceText)
	Page = Page.replace('{:script}', script)
	returnPage = Page.replace('{:profile}', replaceText1)
	return returnPage


# Create the messages page
def createMessages(user, pw):
	f = open("public/home.html")
	Page = f.read()
	f.close()
	# Get the full list of users
	try:
		userList = externalComm.autoGetList(user, pw).read()
		dic = json.loads(userList)
	except Error as e:
		print e

	replaceText = '<ul class="side-nav">' \
	              '<li style="width:100% float:center"><a class="active" href="/">Home</a></li>'

	try:
		for items in dic:
			replaceText += '<li style="width:100%"><a class="side" href="javascript:displayMessages(\'' + dic[items]['username'] + '\')">' + dic[items]['username'] + '</a></li>'
	except Error as e:
		print e

	replaceText1 = '''<div class="name-bar">
                    </div>
                    <div class="messages">
                    </div>
                    <div class="create-message">
                        <form class="form-box" action="/sendMessage" method="post" enctype="multipart/form-data">
                            <textarea class="write-message" name="message"></textarea>
                            <input class="send" id="file" type="file" name="dataFile"/>
                            <button class="send" on-click="sendMessage()" type="submit">Send</button>
                        </form>
                    </div>'''
    
	script = '''<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
				<script src="http://malsup.github.com/jquery.form.js"></script>
				<script src="public/main.js"></script>'''
	Page = Page.replace('{:navActive}', replaceText)
	Page = Page.replace('{:script}', script)
	returnPage = Page.replace('{:profile}', replaceText1)
	return returnPage


# Creste teh divs to show the messages
def createViewMessage(messages, currentUser):
	print messages
	div = ""
	# Need to get the messages and create the divs
	try:
		for items in messages:
			try:
				if items['senderUPI'] == currentUser:
					# Div for my messages displayed
					div += '<div class="message-box-user" name=' + items['time_stamp'] + '>' + items['senderUPI'] + ': ' + items['message'] + '</div>'
				else:
					# Div for guest messages
					div += '<div class="message-box-dest" name=' + items['time_stamp'] + '>' + items['senderUPI'] + ': ' + items['message'] + '</div>'
			except Error as e:
				print e
		return div
	except Error as e:
		print e
	return 0
