from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/restaurants/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
    output = ''
    output += '<h1>%s</h1>' %restaurant.name
    output += '<a href="/restaurants/new_menu/%s/">Add a new menu item</a></br></br>' % restaurant.id
    for i in items:
        output += i.name
        output += '</br>'
        output += i.price
        output += '</br>'
        output += i.description
        output += '</br>'
        output += '<a href="/restaurants/edit_item/%s/%s">Edit</a></br>' % (restaurant.id, i.id) 
        output += '<a href="/restaurants/delete_item/%s/%s/">Delete</a>' % (restaurant.id, i.id)    
        output += '</br></br>'    
    return output

# Task 1: Create route for newMenuItem function here

@app.route('/restaurants/new_menu/<int:restaurant_id>/')
def newMenuItem(restaurant_id):
	#restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    return "page to create a new menu item. Task 1 complete!"

# Task 2: Create route for editMenuItem function here
# note in actual solutions the edit part is on the other side of the url from the id
# like '/restaurants/int/int/edit'
# same with delete
@app.route('/restaurants/edit_item/<int:restaurant_id>/<int:menu_id>/')
def editMenuItem(restaurant_id, menu_id):
    return "page to edit a menu item. Task 2 complete!"

# Task 3: Create a route for deleteMenuItem function here

@app.route('/restaurants/delete_item/<int:restaurant_id>/<int:menu_id>/')
def deleteMenuItem(restaurant_id, menu_id):
    return "page to delete a menu item. Task 3 complete!"

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)



