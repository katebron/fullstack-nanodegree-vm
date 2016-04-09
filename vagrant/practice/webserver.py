from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

#this handler class will extend from the class BaseHTTPRequestHandler
class webServerHandler(BaseHTTPRequestHandler):
	#this handles all GET requests our web server recieives
  def do_GET(self):
  	#in order to figure out which resource we are trying to access, use
  	#simple pattern matching plan that only looks for the ending or our URL
    try:
  	 	#the BaseHTTPRequestHandler provides us with a variable called path,
  	  	#that contains the URL sent by the client to the server as a string
  	  if self.path.endswith("/hello"):
  	  	  #say it's a success
  	    self.send_response(200)
  	    self.send_header('Content-type', 'text/html')
  	    self.end_headers()

  	    output = ""
  	    output += "<html><body>Hello?!</body></html>"
  	      #this sends a message back to the client
  	    self.wfile.write(output)
  	      #just so we can see it in the terminal
  	    print output
  	      #exit if statement with a return command
  	    return
      if self.path.endswith("/hola"):
      

        return

    except IOError:
  	  self.send_error(404, "File not found %s" % self.path)

def main():
  try:
  #create instance of HTTPServer class
  #see https://docs.python.org/2/library/basehttpserver.html
  #the first parameter in the HTTPServer class is server address, the second is RequestHandlerClass
  #server address is a tuple that contains the host and port for our server. 
    port = 8080
    server = HTTPServer(('', port), webServerHandler)
    #port is an integer - put it in a variable. Leaving host as empty string. 
    #the webserverHandler is something we just made up name for and will define later in code - see above    server = HTTPServer(('', port)), webserverHandler)
    print "Web server running on port %s" % port
    #this will keep server constantly listening unless hit control-C or exit application
    server.serve_forever()

  #will enter out of the code if this occurs
  #it's built into Python and triggers if user enters control-C
  except KeyboardInterrupt:  
    print "^C entered, stopping web server..."
    server.socket.close()	

#this goes at end of file to immediately run the main method with the python interpreter executes the script
if __name__ == '__main__':
	main()