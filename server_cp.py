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
# The address we listen for connections on
listen_ip = "0.0.0.0"
listen_port = 1234

import cherrypy
import urllib

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
            data = urllib.urlopen('http://cs302.pythonanywhere.com/report?username=jecc724&password=405d0b44b308be384acfaec2bb23f23b81f59f189e56b6c9e224f2ef0d36d79e&location=0&ip=10.103.137.36&port=10001')
            print data.read()
            Page = "Welcome! This is a test website for COMPSYS302! You have logged in!<br/>"
            return Page
        else:
            raise cherrypy.HTTPRedirect('/login')

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
        print username
        print password
        if (username.lower() == "jecc724") and (password == "tellingmuteCOMPSYS302-2017"):
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
