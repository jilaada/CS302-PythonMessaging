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
