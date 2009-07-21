#!/usr/bin/env python

import sys, httplib
import getopt
import os
import mimetypes
from plist_parser import XmlPropertyListParser, PropertyListParseError
from couchdb import Couch
from subprocess import call

class UploadConfigurationError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

def main(argv):
	"""docstring for main"""
	try:
		opts, args = getopt.getopt(argv, "s:d:a:f:h", ["server=", "db=", "appname=", "filedir=","help"]) 
	except getopt.GetoptError:           
		usage()                          
		sys.exit(2)
	
	server = None
	db = None
	appname = None
	filedir = None
	
	for opt, arg in opts:                
		if opt in ("-h", "--help"):      
			usage()                     
			sys.exit()                  
		elif opt in ("-s", "--server"):                
			server = arg                  
		elif opt in ("-d", "--db"): 
			db = arg
		elif opt in ("-a", "--appname"): 
			appname = arg
		elif opt in ("-f", "--filedir"): 
			filedir = arg
	
	upload(server, db, appname, filedir)

def upload(server=None, db=None, appname=None, filedir=None):
	"""uploads the contents of a local Cappuccino application directory as attachments to a CouchDB design document
	if 'server' is omitted than http://localhost:5984 is assumed
	if 'filedir' is empty, the pwd is assumed as the Cappuccino app root
	if 'db' and 'appname' are omitted then the application name is pulled from the CouchDBName and CouchDBAppName in the info.plist file. If those values are not found, CPBundleName is used. spaces are replaced with dashes"""
	
	if not server:
		server = "http://localhost:5984"	

	if not filedir:
		filedir = os.getcwd()

	if not os.path.exists(filedir):
		raise UploadConfigurationError("filedir does not exist")

	plist_file = filedir + "/Info.plist"
	plist = None
		
	if os.path.exists(plist_file) & os.path.isfile(plist_file):
		parser = XmlPropertyListParser()
		stream = open(plist_file)
		try:
			plist = parser.parse(stream)
		finally:
			stream.close()
			
	plist_couch_db_name = None
	plist_couch_db_app_name = None
	plist_cp_bundle_name = None
			
	if plist:
		plist_couch_db_name = plist["CouchDBName"]
		plist_couch_db_app_name = plist["CouchDBAppName"]
		plist_cp_bundle_name = plist["CPBundleName"]

	if not db:
		if plist_couch_db_name:
			db = plist_couch_db_name
		elif plist_cp_bundle_name:
			db = plist_cp_bundle_name
	
	if not db:
		raise UploadConfigurationError("no db specified")
	
	if not appname:
		if plist_couch_db_app_name:
			appname = plist_couch_db_app_name
		elif plist_cp_bundle_name:
			appname = plist_cp_bundle_name
	
	if not appname:
		raise UploadConfigurationError("no appname specified")

	app_path = "/" + db + "/_design/" + appname
	app_url = server + app_path
	app_doc = "_design/" + appname
	
	print "server    = " + server
	print "appname   = " + appname
	print "db        = " + db
	print "filedir   = " + filedir
	print "app_url   = " + app_url
	
	def is_visible_file(x): return os.path.isfile(x) & (x[0] <> ".")
	
	file_list = filter(is_visible_file, os.listdir(filedir))
	print file_list 
	
	mimetypes.init()
	mimetypes.add_type("application/javascript",".j")
	mimetypes.add_type("text/xml",".plist")
	def mime(x): return mimetypes.types_map[os.path.splitext(x)[1]]
	mime_list = map(mime,file_list)
	print mime_list
	
	c = Couch()
	
	for i in range(len(file_list)):
		print c.get_doc(db,app_doc)
	
def usage():
	print "perk [-s|--server server_name][-d|--db database][-a|--appname application_name][-f|--filedir file_directory][-h|--help]"

if __name__ == "__main__":		
	main(sys.argv[1:])