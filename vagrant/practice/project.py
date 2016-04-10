from flask import Flask
#create an instance of class flask with the name
#the name of the running application is the argument
#anytime we run an application in python,
#a special variable called name gets
#defined for the application and all the imports it uses
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

#wraps function in the app.route decorator.
#if either of these routes gets sent by the 
#browser, this HelloWorld function gets executed
#you can stack decorators in python
#the first one calls the second
#which calls the function below
#useful for having different URLs route 
#to the same place
@app.route('/')
#@app.route('/hello')
#leave trailing slash so flask will render page even if not in url
@app.route('/restaurants/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
	#restaurant = session.query(Restaurant).first()
	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id)
	output = ''
	for i in items:
		output += "<p>"
		output += i.name
		output += '</br>'
		output += i.price
		output += '</br>'
		output += i.description
		output += '</p>'
	return output

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