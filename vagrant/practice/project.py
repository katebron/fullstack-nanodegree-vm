from flask import flask
#create an instance of class flask with the name
#the name of the running application is the argument
#anytime we run an application in python,
#a special variable called name gets
#defined for the application and all the imports it uses
app = Flask(__name__)

#wraps function in the app.route decorator.
#if either of these routes gets sent by the 
#browser, this HelloWorld function gets executed
@app.route('/')
@app.route('hello')
def HelloWorld():
	return "Hello World"

#makes sure script is only run if it comes directly 
#from the python interpreter (and therefore given
# the '__main__ name and not just an imported
#module)
if __name__ == '__main__':
	#server reloads each time it notices a code change
	#also has debugger in browser if things go wrong
	app.debug = True
	#run local server with our application
	app.run(host = '0.0.0.0', port = 5000)