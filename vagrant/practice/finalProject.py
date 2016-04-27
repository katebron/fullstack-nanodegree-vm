from flask import Flask, url_for, render_template, request, redirect, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup2 import Base, Restaurant, MenuItem

app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/restaurants/JSON')
def restaurantsJSON():
	restaurants = session.query(Restaurant).all()
	return jsonify(Restaurants=[i.serialize for i in restaurants])

@app.route('/restaurant/<restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one
	items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id)
	return jsonify(MenuItems=[i.serialize for i in items])	


@app.route('/restaurant/<restaurant_id>/menu/<menu_id>/JSON')
def restaurantMenuItemJSON(restaurant_id, menu_id):
	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one
	item = session.query(MenuItem).filter_by(id=menu_id)
	return jsonify(MenuItem=[i.serialize for i in item])	

@app.route('/')
@app.route('/restaurant')
def showRestaurants():
	#return "This page will show all my restaurants"
	restaurant = session.query(Restaurant).all()
	return render_template('restaurants.html', restaurant=restaurant)

@app.route('/restaurant/new', methods=['GET', 'POST'])
def newRestaurant():
	if request.method == 'POST':
		newItem = Restaurant(name = request.form['newRName'])
		session.add(newItem)
		session.commit()
		return redirect(url_for('showRestaurants'))
	else:
		return render_template('newrestaurant.html')

@app.route('/restaurant/<restaurant_id>/edit', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
	if request.method == 'POST':
		restaurant.name = request.form['newName']
		session.add(restaurant)
		session.commit()
		return redirect(url_for('editRestaurant', restaurant_id=restaurant.id))
	else:		
		items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
		return render_template('editrestaurant.html', items=items, restaurant=restaurant)

@app.route('/restaurant/<restaurant_id>/delete', methods=['GET','POST'])
def deleteRestaurant(restaurant_id):
	toDelete = session.query(Restaurant).filter_by(id=restaurant_id).one()
	if request.method == 'POST':
		session.delete(toDelete)
		session.commit()
		itemsToDelete = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
		for item in itemsToDelete:
			session.delete(item)
			session.commit()
		return redirect(url_for('showRestaurants'))
	else:
		return render_template('deleterestaurant.html', restaurant = toDelete)
	
	
@app.route('/restaurant/<restaurant_id>')
@app.route('/restaurant/<restaurant_id>/menu')
def showMenu(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
	items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
	return render_template('restaurant.html', items=items, restaurant=restaurant)
	return "This page is the menu for restaurant %s" % restaurant_id

@app.route('/restaurant/<restaurant_id>/menu/new', methods=['GET','POST'])
def newMenuItem(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
	if request.method == 'POST':
		newItem = MenuItem(name = request.form['newItem'], restaurant_id = restaurant.id, 
			description = request.form['description'], price = request.form['price'])
		session.add(newItem)
		session.commit
		return redirect(url_for('showMenu', restaurant_id = restaurant.id))
	else:
		return render_template('newmenuitem.html', restaurant = restaurant)



@app.route('/restaurant/<restaurant_id>/menu/<menu_id>/edit', methods=['GET','POST'])
def editMenuItem(restaurant_id, menu_id):
	restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
	menuItem = session.query(MenuItem).filter_by(id=menu_id).one()
 	if request.method == 'POST':
		menuItem.name = request.form['name']
		menuItem.description = request.form['description']
		menuItem.price = request.form['price']
		session.add(menuItem)
		session.commit()
		return redirect(url_for('showMenu', restaurant_id = restaurant.id))
	else:
		return render_template('editmenuitem.html', restaurant = restaurant, item = menuItem)


@app.route('/restaurant/<restaurant_id>/menu/<menu_id>/delete', methods=['GET','POST'])
def deleteMenuItem(restaurant_id, menu_id):
	menuItem = session.query(MenuItem).filter_by(id=menu_id).one()
	if request.method == 'POST':
		session.delete(menuItem)
		session.commit()
		return redirect(url_for('showMenu', restaurant_id = restaurant_id))
	else:
		return render_template('deletemenuitem.html', restaurant_id = restaurant_id, item = menuItem)
	


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)