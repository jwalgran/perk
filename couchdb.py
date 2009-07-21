import httplib
import simplejson

def pretty_print_json_response(response):
	"""cleanly formats a HTTPResponse object with JSON content"""
	
	# HTTPResponse instance -> Python object -> str
	print simplejson.dumps(simplejson.loads(response.read()), sort_keys=True, indent=4)

class Couch:
	"""Basic wrapper class for operations on a couchDB"""
	
	def __init__(self, host="localhost", port=5984, options=None):
		self.host = host
		self.port = port

	def connect(self):
		return httplib.HTTPConnection(self.host, self.port) # No close()

    # Database operations

	def create_db(self, db_name):
		"""Creates a new database on the server"""

		r = self.put(''.join(['/',db_name,'/']), {"Accept": "application/json"}, "")
		pretty_print_json_response(r)

	def delete_db(self, db_name):
		"""Deletes the database on the server"""

		r = self.delete(''.join(['/',db_name,'/']))
		pretty_print_json_response(r)

	def list_db(self):
		"""List the databases on the server"""

		pretty_print_json_response(self.get('/_all_dbs', {"Accept": "application/json"}))

	def info_db(self, db_name):
		"""Returns info about the couchDB"""
		
		r = self.get(''.join(['/', db_name, '/']), {"Accept": "application/json"})
		pretty_print_json_response(r)

    # Document operations

	def list_docs(self, db_name):
		"""List all documents in a given database"""

		r = self.get(''.join(['/', db_name, '/', '_all_docs']), {"Accept": "application/json"})
		pretty_print_json_response(r)

	def get_doc(self, db_name, doc_id):
		"""Gets a document in a given database"""
		r = self.get(''.join(['/', db_name, '/', doc_id,]), {"Accept": "application/json"})
		pretty_print_json_response(r)

	def save_doc(self, db_name, body, doc_id=None):
		"""Save/create a document to/in a given database"""
		if docId:
			r = self.put(''.join(['/', db_name, '/', doc_id]), {"Content-type": "application/json"}, body)
		else:
			r = self.post(''.join(['/', db_name, '/']), {"Content-type": "application/json"}, body)
		
		pretty_print_json_response(r)

	def delete_doc(self, db_name, doc_id):
		# XXX Crashed if resource is non-existent; not so for DELETE on db. Bug?
		# XXX Does not work any more, on has to specify an revid 
		#     Either do html head to get the recten revid or provide it as parameter
		r = self.delete(''.join(['/', db_name, '/', docId]))
		pretty_print_json_response(r)

	# Attachment operations
	
	def save_attachment(self, db_name, doc_id, file_path, attach_path=None, mime_type=None):
		"""Attaches a file to a document. If the doc_id does not exist, a new one will be created"""
		pass
		
	def delete_attachment(self, db_name, doc_id, attach_path):
		"""Deletes an attachment from a document"""
		pass

    # Basic http methods

	def get(self, uri, headers):
		c = self.connect()
		c.request("GET", uri, None, headers)
		return c.getresponse()

	def post(self, uri, headers, body):
		c = self.connect()
		c.request('POST', uri, body, headers)
		return c.getresponse()

	def put(self, uri, headers, body):
		c = self.connect()
		c.request("PUT", uri, body, headers)
		return c.getresponse()

	def delete(self, uri):
		c = self.connect()
		c.request("DELETE", uri)
		return c.getresponse()
		