__metaclass__ = type


class System():


	def __init__(self):
		self.current_user = None
		self.credentials = None
		self.current_environment = None

	def connect(self, credentials):
		self.validate_credentials(credentials)

	def get_environment(self, user=None):
		pass

	def list_enviroments(self, user=None):
		# Connect to the server as a user (defaults to currently logged 
		# in user) and returns a list of environment objects. 

		return (environments)	
	
	def _get_user(self, user=None):
		if user == None: 
			user = self.current_user
			return None
