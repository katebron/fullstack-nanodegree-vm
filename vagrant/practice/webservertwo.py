from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
#to decifer messages sent from the server, import common gateway interface (cgi)
import cgi

class webServerHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		try:
			if self.path.endswith("/hello"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				output = ""
                output += "<html><body>"
                output += "<h1>Hello!</h1>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
                output += "</body></html>"
				self.wfile.write(output)
				print output
				return
			if self.path.endswith("/hola"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				output = ""
				output += "<html><body>&#161Hola<a href='/hello' >Back to hello</a>"
				output += '''<form method='POST' enctype = 'multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name = 'message' type='text'><input type = 'submit' value='Submit'></form>'''
                output += "</body></html>"
				self.wfile.write(output)
				print output
				return	
		except IOError:
			self.send_error(404, 'File Not Found: %s' % self.path)

	def do_POST(self):
		try:
			self:send_response(301)
			self.end_headers()
            #cgi.parse_header function parses an html form header such as content-type into
            # a main value a main value and dictonary parameters
			ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
			#if it's form data being recieved - 
			if ctype == 'multipart/form-data'
				#create variable fields which collects all the fields in a form
				fields=cgi.parse_multipart(self.rfile, pdict)
				#make a variable called messagecontent to get a value of a specific field,
				# or set of fields, and store them in an array
				messagecontent = fields.get('message')

				output = ""
				output += "<html><body>"
				output += "<h2>Ok, how about this:</h2>"
				#returns first value of the array that was created
				output += "<h1> %s </h1>" % messagecontent[0]
                
                output += "<form method='POST' enctype = 'multipart/form-data' action='/hello'>"
                output += "<h2>What would you like me to say?</h2>"
                #you want the message input name to correspond with the fields.get('message')
                output += "<input name = 'message' type='text'>"
                output += "<input type = 'submit' value='Submit'></form>"
                self.wfile.write(output)
                print output
       
		except:		
			pass
def main():
	try:
		port = 8080
		server = HTTPServer(('', port), webServerHandler)
		print "Web Server running on port %s"  % port
		server.serve_forever()
	except KeyboardInterrupt:
		print " ^C entered, stopping web server...."
		server.socket.close()

if __name__ == '__main__':
	main()