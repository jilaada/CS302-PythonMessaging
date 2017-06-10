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
	f = open("public/profile.html")
	Page = f.read()
	f.close()
	# Get data from the database about the user
	profileData = databaseFunctions.getProfile(user)
	returnPage = Page.replace('{:session}', user)
	return returnPage


# Create the messages page
def createMessages(user, pw):
	f = open("public/messages.html")
	Page = f.read()
	f.close()
	# Get the full list of users
	returnPage = Page.replace('{:session}', user)
	return returnPage


# Creste teh divs to show the messages
def createViewMessage(messages, currentUser):
	div = ""
	# Need to get the messages and create the divs
	try:
		for items in messages:
			print items['message_type']
			try:
				messagetype = str(items['message_type'])
				messagetype = messagetype.split("/")
			except TypeError as e:
				messagetype = "unknownType"
			try:
				if items['senderUPI'] == currentUser:
					# Div for my messages displayed
					print messagetype[1]
					if messagetype[0] == "text":
						div += '<div class="message-box-user" name=' + items['time_stamp'] + '>' + items['senderUPI'] + ': ' + items['message'] + '</div>'
					elif messagetype[0] == "video":
						div += '<div class="message-box-user" name=' + items['time_stamp'] + '>' + items['senderUPI'] + ': <video width="auto" height="auto" controls><source src="public/downloads/' + items['message'] + '"></source></video></div>'
					elif messagetype[0] == "image":
						div += '<div class="message-box-user" name=' + items['time_stamp'] + '>' + items['senderUPI'] + ': <img src="public/downloads/' + items['message'] + '" style="width:auto;height:auto;"></img></div>'
					elif messagetype[0] == "application":
						div += '<div class="message-box-user" name=' + items['time_stamp'] + '>' + items['senderUPI'] + ': <a href="public/downloads/' + items['message'] + '" >' + items['message'] + '</a></div>'
					else:
						div += '<div class="message-box-user" name=' + items['time_stamp'] + '>' + items['senderUPI'] + ': ' + items['message'] + '</div>'
				else:
					# Div for guest messages
					if messagetype[0] == "text":
						div += '<div class="message-box-dest" name=' + items['time_stamp'] + '>' + items['senderUPI'] + ': ' + items['message'] + '</div>'
					elif messagetype[0] == "video":
						div += '<div class="message-box-dest" name=' + items['time_stamp'] + '>' + items['senderUPI'] + ': <video width="auto" height="auto" controls><source src="public/downloads/' + items['message'] + '"></source></video></div>'
					elif messagetype[0] == "image":
						div += '<div class="message-box-dest" name=' + items['time_stamp'] + '>' + items['senderUPI'] + ': <img src="public/downloads/' + items['message'] + '" style="width:auto;height:auto;"></img></div>'
					elif messagetype[0] == "application":
						div += '<div class="message-box-dest" name=' + items['time_stamp'] + '>' + items['senderUPI'] + ': <a href="public/downloads/' + items['message'] + '" >' + items['message'] + '</a></div>'
					else:
						div += '<div class="message-box-dest" name=' + items['time_stamp'] + '>' + items['senderUPI'] + ': ' + items['message'] + '</div>'
			except Error as e:
				print e
		return div
	except Error as e:
		print e
	return 0


def createUserList(user, pw):
	try:
		userList = externalComm.autoGetList(user, pw).read()
		dic = json.loads(userList)
	except Error as e:
		print e
	
	replaceText = '<ul class="side-nav">' \
	              '<li style="width:100% id="Home" float:center"><a class="active" href="/">Home</a></li>'

	try:
		for items in dic:
			replaceText += '<li style="width:100%"><a class="side" id="' + dic[items]['username'] + '" href="javascript:displayMessages(\'' + dic[items]['username'] + '\')">' + dic[items]['username'] + '</a></li>'
	except Error as e:
		print e
	return replaceText
