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

# The address we listen for connections on
listen_ip = "0.0.0.0"
try:
    listen_port = int(sys.argv[1])
except (IndexError, TypeError):
    listen_port = 1234

class MainApp(object):
    # CherryPy Configuration - uses a CherryPy config dictionary
    _cp_config = {'tools.encode.on': True, 
                  'tools.encode.encoding': 'utf-8',
                  'tools.sessions.on' : 'True',
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
        except KeyError: #There is no username
            
            Page += "Click here to <a href='login'>login</a>."
        #return urllib2.urlopen("file:///home/jilada/Desktop/COMPSYS302-PYTHON/uoa-cs302-2017-jecc724/index.html")
        return Page



    #The login page fo rthe sever - currently configured to login into the compsys server via hardcoding my credentials
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
        if (error == 0):
            cherrypy.session['username'] = username;
            Page = "Welcome! This is a test website for COMPSYS302! You have logged in!<br/>"
            return Page
        else:
            raise cherrypy.HTTPRedirect('/login')

    
    @cherrypy.expose
    def getList(self):
        # Check for a valid username
        username = cherrypy.session.get('username')
        hashpw = cherrypy.session.get('password')
        if (username == None):
            pass
        else:
            data = urllib.urlopen('http://cs302.pythonanywhere.com/getList?username=' + username + '&password=' + hashpw + '&enc=0&json=0')
            print data.read() 
        raise cherrypy.HTTPRedirect('/')

    @cherrypy.expose
    def signout(self):
        """Logs the current user out, expires their session"""
        username = cherrypy.session.get('username')
        if (username == None):
            pass
        else:
            cherrypy.lib.sessions.expire()
        raise cherrypy.HTTPRedirect('/')

        
    def authoriseUserLogin(self, username, password):
        # Get hash of password
        hashpw = hashlib.sha256(password).hexdigest()
        cherrypy.session['password'] = hashpw;
        data = urllib.urlopen('http://cs302.pythonanywhere.com/report?username=' + username + '&password=' + hashpw + '&location=2&ip=127.0.0.1&port=10001')
        if (data.read() == "0, User and IP logged"):
            return 0
        else:
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
runMainApp()
