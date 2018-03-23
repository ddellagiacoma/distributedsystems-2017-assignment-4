# coding=utf-8
#------------------------------------------------------------------------------------------------------
# TDA596 Labs - Server Skeleton
# server/server.py
# Input: Node_ID total_number_of_ID
# Student Group: 37
# Student name: Daniele Dellagiacoma
#------------------------------------------------------------------------------------------------------
# Import various libraries
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler # Socket specifically designed to handle HTTP requests
import sys # Retrieve arguments
from urlparse import parse_qs # Parse POST data
from httplib import HTTPConnection # Create a HTTP connection, as a client (for POST requests to the other vessels)
from urllib import urlencode # Encode POST content into the HTTP header
from codecs import open # Open a file
from threading import  Thread # Thread Management
import ast # Process trees of the Python abstract syntax grammar
from collections import Counter # Count hashable objects
#------------------------------------------------------------------------------------------------------

# Global variables for HTML templates
vote_frontpage_template = ""
vote_result_template = ""

#------------------------------------------------------------------------------------------------------
# Static variables definitions
PORT_NUMBER = 80
STUDENT_NAME = "Daniele Dellagiacoma"
#------------------------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
class BlackboardServer(HTTPServer):
#------------------------------------------------------------------------------------------------------
	def __init__(self, server_address, handler, node_id, vessel_list):
		# Call the super init
		HTTPServer.__init__(self, server_address, handler)
		# Collect values received in a vector
		self.store = {}
		# Keep a variable of the next id to insert
		self.current_key = -1
		# Our own ID (IP is 10.1.0.ID)
		self.vessel_id = vessel_id
		# The list of other vessels
		self.vessels = vessel_list
		# Colllect the vector of the other vessel
		self.results = {}
		# If a vector is byzantine or not
		self.byzantine = False
		# Result taking into consideraton the majority of vote
		self.final_vector=[]
#------------------------------------------------------------------------------------------------------
	# Contact a specific vessel with a set of variables to transmit to it
	def contact_vessel(self, vessel_ip, path, vector):
		# The Boolean variable that will be returned
		success = False
		# The variables must be encoded in the URL format, through urllib.urlencode
		post_content = urlencode({'id': self.vessel_id, 'vector': vector})
		# The HTTP header must contain the type of data transmitted, here URL encoded
		headers = {"Content-type": "application/x-www-form-urlencoded"}
		# Try to catch errors when contacting the vessel
		try:
			# Contact vessel:PORT_NUMBER since they all use the same port
			# Set a timeout to 30 seconds, after which the connection fails if nothing happened
			connection = HTTPConnection("%s:%d" % (vessel_ip, PORT_NUMBER), timeout = 30)
			# Only use POST to send data (PUT and DELETE not supported)
			action_type = "POST"
			# Send the HTTP request
			connection.request(action_type, path, post_content, headers)
			# Retrieve the response
			response = connection.getresponse()
			# Check the status, the body should be empty
			status = response.status
			# If it receive a HTTP 200 - OK
			if status == 200:
				success = True
		# Catch every possible exceptions
		except Exception as e:
			print("Error while contacting %s" % vessel_ip)
			# Print the error given by Python
			print(e)

		# Return whether it succeeded or not
		return success
#------------------------------------------------------------------------------------------------------
	# Send a received value to all the other vessels of the system
	def propagate_value_to_vessels(self, path, vector):
		# Iterate through the vessel list
		for vessel in self.vessels:
			# Should not send it to our own IP, or it would create an infinite loop of updates
			if vessel != ("10.1.0.%s" % self.vessel_id):
				# Try again until the request succeed
				while (True):
					if self.contact_vessel(vessel, path, vector):
						break
#------------------------------------------------------------------------------------------------------
	# Send out different votes to the honest nodes in order to break agreement
	def propagate_value_to_vessels_byzantine(self, path, result_vote):
		i = 0
		# Iterate through the vessel list
		for vessel in self.vessels:
			# Should not send it to our own IP, or it would create an infinite loop of updates
			if vessel != ("10.1.0.%s" % self.vessel_id):
				# If True sends a POST request on "/propagate/attack"
				if result_vote[i]:
					# Try again until the request succeed
					while (True):
						if self.contact_vessel(vessel, path + 'attack', self.store):
							break
				# If False sends a POST request on "/propagate/retreat"
				else:
					# Try again until the request succeed
					while (True):
						if self.contact_vessel(vessel, path + 'retreat', self.store):
							break
				i = i + 1
#------------------------------------------------------------------------------------------------------
	# Send to other vessels a vector of Byzantine votes
	def propagate_value_to_vessels_byzantine2(self, path, result_vectors):
		i = 0
		dict = {}
		# Iterate through the vessel list
		for vessel in self.vessels:
			# Should not send it to our own IP, or it would create an infinite loop of updates
			if vessel != ("10.1.0.%s" % self.vessel_id):
				arr = result_vectors[i]
				j=1
				# Convert the array of byzantine votes to a dictionary
				for a in arr:
					dict [j] = a
					j=j+1
				# Try again until the request succeed
				while (True):
					if self.contact_vessel(vessel, path, dict):
						break
			i = i + 1
#------------------------------------------------------------------------------------------------------


#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
# This class implements the logic when a server receives a GET or POST request
# It can access to the server data through self.server.*
# i.e. the store is accessible through self.server.store
# Attributes of the server are SHARED accross all request hqndling/ threads!
class BlackboardRequestHandler(BaseHTTPRequestHandler):
#------------------------------------------------------------------------------------------------------
	# Fill the HTTP headers
	def set_HTTP_headers(self, status_code = 200):
		# Set the response status code (200 if OK, something else otherwise)
		self.send_response(status_code)
		# Set the content type to HTML
		self.send_header("Content-type", "text/html")
		# Close headers
		self.end_headers()
#------------------------------------------------------------------------------------------------------
	# POST request must be parsed through urlparse.parse_QS, since the content is URL encoded
	def parse_POST_request(self):
		post_data = ""
		# Parse the response, the length of the content is needed
		length = int(self.headers['Content-Length'])
		# Parse the content using parse_qs
		post_data = parse_qs(self.rfile.read(length), keep_blank_values = 1)
		# Return the data
		return post_data
#------------------------------------------------------------------------------------------------------	
#------------------------------------------------------------------------------------------------------
# Request handling - GET
#------------------------------------------------------------------------------------------------------
	# This function contains the logic executed when this server receives a GET request
	# This function is called AUTOMATICALLY upon reception and is executed as a thread!
	def do_GET(self):
		print("Receiving a GET on path %s" % self.path)
		# Check which path was requested and call the right logic based on it
		if self.path == "/":
			self.do_GET_Index()
		elif self.path == "/vote/result":
			self.do_GET_Result()
		else:
			# In any other case 
			self.wfile.write("The requested URL does not exist on the server")
#------------------------------------------------------------------------------------------------------
# GET logic - specific path: "/"
#------------------------------------------------------------------------------------------------------
	def do_GET_Index(self):

		try:
			# Set the response status code to 200 (OK)
			self.set_HTTP_headers(200)

			# Write the HTML file on the browser
			self.wfile.write(vote_frontpage_template)

		# Catch every possible exception
		except Exception as e:
			# Print error given by Python on the server console
			print(e)
			# Write the error given by Python on the browser
			self.wfile.write("The following problem has been encountered: " + str(e) + "\n. Please try to refresh the page. \n")
			# Set the response status code to 400 (Bad Request)
			self.set_HTTP_headers(400)
#------------------------------------------------------------------------------------------------------
# GET logic - specific path: "/vote/result"
#------------------------------------------------------------------------------------------------------
	def do_GET_Result(self):

		try:
			# Set the response status code to 200 (OK)
			self.set_HTTP_headers(200)

			# Vote results after Byzantine agreement. Show Individual nodes results and final result
			html_reponse = vote_result_template % (self.server.results, self.server.final_vector)

			# Write the results on the browser
			self.wfile.write(html_reponse)

			# Check if a vessel has received all votes
			if (len(self.server.store) == len(self.server.vessels)):
				# Start the second step of the algorithm
				self.step_two()

		# Catch every possible exception
		except Exception as e:
			# Print error given by Python on the server console
			print(e)
			# Write the error given by Python on the browser
			self.wfile.write("The following problem has been encountered: " + str(e) + "\n. Please try to refresh the page. \n")
			# Set the response status code to 400 (Bad Request)
			self.set_HTTP_headers(400)
#------------------------------------------------------------------------------------------------------
	# Step 2 of the algorithm, when a vessel has received all votes
	def step_two(self):
		# If honest, it sends to other vessels a vector of all votes received
		if (not self.server.byzantine):
			thread = Thread(target=self.server.propagate_value_to_vessels, args=("/vote/result", self.server.store))
			thread.daemon = True
			# Start the thread
			thread.start()
		# If Byzantine, it sends to other vessels a vector of Byzantine votes
		else:
			self.compute_byzantine_vote_round2(len(self.server.vessels) - 1, len(self.server.vessels), False)
#------------------------------------------------------------------------------------------------------


#------------------------------------------------------------------------------------------------------
# Request handling - POST
#------------------------------------------------------------------------------------------------------
	# This function contains the logic executed when this server receives a POST request
	# This function is called AUTOMATICALLY upon reception and is executed as a thread!
	def do_POST(self):
		print("Receiving a POST on %s" % self.path)

		try:
			# Variable used to check if the message needs to be propagated to the other servers
			retransmit = False
			# Call the method to parse the data received from the POST request
			# Save the data in a dictionary, e.g. {'id':['1'], 'vector':['{1: {1: False, 2: True}, 2: {1: False, 2: True}}']}
			parameters = self.parse_POST_request()

			# Check which path was requested and call the right logic based on it
			if self.path == "/vote/attack" or self.path == "/vote/retreat":
				self.do_POST_Honest(parameters)
				retransmit = True
			elif self.path == "/propagate/attack" or self.path == "/propagate/retreat":
				self.do_POST_Honest(parameters)
			elif self.path == "/vote/byzantine":
				self.server.byzantine = True
				self.server.store[self.server.vessel_id] = False
				self.compute_byzantine_vote_round1(len(self.server.vessels) - 1, len(self.server.vessels), False)
			elif self.path == "/vote/result":
				self.save_vectors_and_agreement(parameters)
			else:
				# In any other case 
				self.wfile.write("The requested URL does not exist on the server")

			# Set the response status code to 200 (OK)
			self.set_HTTP_headers(200)

		# Catch every possible exception
		except Exception as e:
			# Print error given by Python on the server console
			print(e)
			# Set retransmit to False avoiding the further propagation of other errors
			retransmit = False
			# Set the response status code to 400 (Bad Request)
			self.set_HTTP_headers(400)

		# If True the message needs to be propagate to the other servers
		if retransmit:
			# do_POST send the message only when the function finishes
			# Create threads to do some heavy computation
			thread = Thread(target=self.server.propagate_value_to_vessels, args=(self.path.replace("vote","propagate"), ""))
			thread.daemon = True
			# Start the thread
			thread.start()
#------------------------------------------------------------------------------------------------------
# POST Logic - specific path: "/vote/attack", "/vote/retreat", "/propagate/attack", "/propagate/retreat"
#------------------------------------------------------------------------------------------------------
	def do_POST_Honest(self, parameters):
		# Check which path was requested and call the right logic based on it
		path_segments = (self.path).split("/")
		if path_segments[1] == "vote":
		# Save the vote received from the other vessels, i.e. True if attack, False if retreat
			if path_segments[2] == "attack":
				self.server.store[self.server.vessel_id] = True
			elif path_segments[2] == "retreat":
				self.server.store[self.server.vessel_id] = False
		elif path_segments[1] == "propagate":
			if path_segments[2] == "attack":
				self.server.store[int(parameters['id'][0])] = True
			elif path_segments[2] == "retreat":
				self.server.store[int(parameters['id'][0])] = False
#------------------------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------------------
# Simple methods that the byzantine node calls to decide what to vote.
#------------------------------------------------------------------------------------------------------
	# Compute byzantine votes for round 1, by trying to create a split decision.
	# input: 
	#	number of loyal nodes,
	#	number of total nodes,
	#	Decision on a tie: True or False 
	# output:
	#	Send to the loyal nodes a list with votes in the form [True, False, True, .....]
	def compute_byzantine_vote_round1(self, no_loyal, no_total, on_tie):
		result_vote = []
		for i in range(0, no_loyal):
			if i % 2 == 0:
				result_vote.append(not on_tie)
			else:
				result_vote.append(on_tie)
		# Create threads to do some heavy computation
		thread = Thread(target=self.server.propagate_value_to_vessels_byzantine, args=("/propagate/", result_vote))
		thread.daemon = True
		# Start the thread
		thread.start()
#------------------------------------------------------------------------------------------------------
	# Compute byzantine votes for round 2, trying to swing the decision
	# on different directions for different nodes.
	# input: 
	#	number of loyal nodes,
	#	number of total nodes,
	#	Decision on a tie: True or False
	# output:
	#	Send to every one of the loyal ones a list
	#	where every element is a the vector
	#	in the form [[True, ...], [False, ...], ...]
	def compute_byzantine_vote_round2(self, no_loyal, no_total, on_tie):
		result_vectors = []
		for i in range(0, no_loyal):
			if i % 2 == 0:
				result_vectors.append([on_tie] * no_total)
			else:
				result_vectors.append([not on_tie] * no_total)
		# Create threads to do some heavy computation
		thread = Thread(target=self.server.propagate_value_to_vessels_byzantine2, args=("/vote/result", result_vectors))
		thread.daemon = True
		# Start the thread
		thread.start()
#------------------------------------------------------------------------------------------------------
	# Save the vectors received from the other vessel and compute the majority vote result
	def save_vectors_and_agreement(self, parameters):
		# Add the vector received from the other vessels to the result vector
		self.server.results[int(parameters['id'][0])] = ast.literal_eval(parameters['vector'][0])

		final_res = []
		# Iterate through the result vector
		for i in range (1, len(self.server.results) + 2):
			tmp = []
			# Save in a tmp variable the elements with the same key
			tmp = self.myprint(self.server.results, i, tmp)
			# Call the function to calculate the max number of occurences in a list
			most = self.most_common(tmp)
			# If the max number of occurences is (len(self.server.results) / 2), it means that True and False occur the same number of times
			if most[1] == (len(self.server.results) / 2):
				final_res.append('UNKNOWN')
			else:
				final_res.append(most[0])

		# Save the majority vote result
		self.server.final_vector = final_res
#------------------------------------------------------------------------------------------------------
	# Recursive function to extrapolate from a dictionary of dictionary the elements with the same key
	def myprint(self, d, key, result):
		for k, v in d.iteritems():
			if isinstance(v, dict):
				self.myprint(v, key, result)
			elif (k == key):
				result.append(v)
		return result
#------------------------------------------------------------------------------------------------------
	# Return the element that occurred the highest number of times in a list and its number of occurences
	def most_common(self, lst):
		data = Counter(lst)
		return data.most_common(1)[0]
#------------------------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------------------
# Execute the code
if __name__ == '__main__':

	try:
		# Open all the HTML files
		file_frontpage = open("server/vote_frontpage_template.html", 'rU')
		file_result = open("server/vote_result_template.html", 'rU')
		
		# Read the templates from the corresponding HTML files
		vote_frontpage_template = file_frontpage.read()
		vote_result_template = file_result.read()

		# Close all the HTML template files
		file_frontpage.close()
		file_result.close()

	except Exception as e:
		print("Problem with the HTML template files: %s" % e)

	vessel_list = []
	vessel_id = 0

	# Checking the arguments
	if len(sys.argv) != 3: # 2 args, the script and the vessel name
		print("Arguments: vessel_ID number_of_vessels")
	else:
		# We need to know the vessel IP
		vessel_id = int(sys.argv[1])
		# Write the other vessels IP, based on the knowledge of their number
		for i in range(1, int(sys.argv[2]) + 1):
			# Add server itself, test in the propagation
			vessel_list.append("10.1.0.%d" % i)

	# Create server
	server = BlackboardServer(('', PORT_NUMBER), BlackboardRequestHandler, vessel_id, vessel_list)
	print("Starting the server on port %d" % PORT_NUMBER)

	# Run server
	try:
		server.serve_forever()
	except KeyboardInterrupt:
		server.server_close()
		print("Stopping Server")
#------------------------------------------------------------------------------------------------------
