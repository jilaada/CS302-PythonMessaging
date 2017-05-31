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
            print(sqlite3.version)
        except Error as e:
            print(e)
        finally:
            conn.close()

        # This section determines if there is a database
        conn = self.connectDatabase()
        if conn is not None:
            self.createTable(conn)
            self.addRegisteredUsers(conn)
        return Page

    # =====================
    # Database Manipulation
    # =====================

    # Function that will take a connected database and add the table headers
    def createTable(self, conn):
        sql_create_table_usersRegisters = "CREATE TABLE IF NOT EXISTS userRegister (id INTEGER PRIMARY KEY AUTOINCREMENT, upi TEXT, ip TEXT, public_key TEXT, location INTEGER, last_login TEXT); "
        c = conn.cursor()
        c.execute(sql_create_table_usersRegisters)
        conn.commit()
        pass

    # Function that will take a connected database and add the registered users to the list
    def addRegisteredUsers(self, conn):
        dest = "http://cs302.pythonanywhere.com/listUsers"
        userList = urllib.urlopen(dest)
        list = tuple(userList.read().split(","))
        for user in list:
            self.addUser(conn, user)
        pass

    # Function will add single users one at a time to the database
    def addUser(self, conn, user):
        sql_insert_upi = 'INSERT INTO userRegister(upi) VALUES(?) '
        c = conn.cursor()
        c.execute(sql_insert_upi, (user,))
        conn.commit()
        pass



    # The main web page for the website. The user is directed here when they first open the browser
    @cherrypy.expose
    def usersOnline(self):
        Page = "Here are the people who are currently online!<br/>"
        users = self.getList()
        Page += users.read()
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
            cherrypy.session['username'] = username;
            Page = "Welcome! This is a test website for COMPSYS302! You have logged in!<br/>"
            return Page
        else:
            raise cherrypy.HTTPRedirect('/login')



    @cherrypy.expose
    def signout(self):
        """Logs the current user out, expires their session"""
        username = cherrypy.session.get('username')
        if username is None:
            pass
        else:
            cherrypy.lib.sessions.expire()
        raise cherrypy.HTTPRedirect('/')


    # =================
    # Private functions  
    # =================
    
	# Function that will allow the user to get a list of the current users online and display them in the terminal
    def getList(self):
        # Check for a valid username
        username = cherrypy.session.get('username')
        hashpw = cherrypy.session.get('password')
        Page = "Here is a list of all the users!<br/>"
        if username is None:
            pass
        else:
            data = urllib.urlopen('http://cs302.pythonanywhere.com/getList?username=' + username + '&password=' + hashpw + '&enc=0&json=1')
            # Need another functions that will write and read from the database
        return data




    def authoriseUserLogin(self, username, password):
        # Get hash of password
        hashpw = hashlib.sha256(password).hexdigest()
        cherrypy.session['password'] = hashpw;
        ipadd = cherrypy.request.remote.ip
        dataip = json.loads(urllib.urlopen("http://ip.jsontest.com/").read())
        print dataip["ip"]
        data = urllib.urlopen('http://cs302.pythonanywhere.com/report?username=' + username + '&password=' + hashpw + '&location=0&ip=' + '10.103.137.64' + '&port=10001')
        if data.read() == "0, User and IP logged":
            return 0
        else:
            return 1




    def connectDatabase(self):
        try:
            conn = sqlite3.connect("database.db")
            cherrypy.session['database'] = conn
        except Error as e:
            return e
        return conn

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
runMainApp()
