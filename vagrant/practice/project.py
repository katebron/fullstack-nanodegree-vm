from flask import Flask, url_for, render_template, request, redirect, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup2 import Base, Restaurant, MenuItem

app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

#Outputs data only for API. All menu items for a given restaurant
@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def restaurantMenuJson(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()	
	items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
	#instead of returning a template, return jsonify class
	#with a loop to serialize all of the entries
	return jsonify(MenuItems=[items.serialize])

#Outputs data only for API: one menu item for a given restaurant
@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def MenuItemJson(restaurant_id, menu_id):
	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()	
	items = session.query(MenuItem).filter_by(id = menu_id).one()
	#instead of returning a template, return jsonify class
	#with a loop to serialize all of the entries
	return jsonify(MenuItems=[items.serialize])	

@app.route('/')
@app.route('/restaurants/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
    #render_template is the function to bring in the menu.html template, 
    #plus the queries so the template has access to these variables.
    return render_template('menu.html', restaurant=restaurant, items=items)

# Task 1: Create route for newMenuItem function here

@app.route('/restaurants/new_menu/<int:restaurant_id>/', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
	if request.method == 'POST':
		newItem = MenuItem(name = request.form['name'], restaurant_id =  restaurant_id)
		session.add(newItem)
		session.commit()
		flash("New menu item added!")
		return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
	else:
		return render_template('newmenuitem.html', restaurant_id = restaurant_id)

# Task 2: Create route for editMenuItem function here
# note in actual solutions the edit part is on the other side of the url from the id
# like '/restaurants/int/int/edit'
# same with delete
# this doesn't actually work bc i don't have an edit menu template
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit',
           methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    editedItem = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        session.add(editedItem)
        session.commit()
        flash("Menu item edited!")
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        return render_template(
            'editmenuitem.html', restaurant_id=restaurant_id, menu_id=menu_id, item=editedItem)
# Task 3: Create a route for deleteMenuItem function here

@app.route('/restaurants/delete_item/<int:restaurant_id>/<int:menu_id>/', methods=['GET','POST'])
def deleteMenuItem(restaurant_id, menu_id):
	itemToDelete = session.query(MenuItem).filter_by(id=menu_id).one()
	if request.method == 'POST':
		session.delete(itemToDelete)
		session.commit()
		flash("Menu item deleted!")
		return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
	else:
		#couldn't get the instructor soln to work
		return render_template('deletemenuitem.html', item = itemToDelete, restaurant_id = restaurant_id)	
    #return "page to delete a menu item. Task 3 complete!"

if __name__ == '__main__':
	#make a secret key so can have a session
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host='0.0.0.0', port=5000)



