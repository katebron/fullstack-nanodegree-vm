from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem
engine = create_engine('sqlite:///restaurantmenub.db')
Base.metadata.bind = engine

'''creates a mode of communication between code executions and the engine we just created'''
DBSession = sessionmaker(bind = engine)
'''session is how sqlalchemy communicates - allows us to write down all the doce but not execute until we call a commit
this is creating an instance of DBSession and caling it session:
'''
session = DBSession()
'''the session object gives you a staging zone for all of the objects loaded into DBSession. An
 Any changes made won't be persisted until you call session.commit
'''

myFirstRestaurant = Restaurant(name = "Pizza Palace")
session.add(myFirstRestaurant) 
'''change in staging zone to commit'''
session.commit()

'''can query to see if it worked:'''
session.query(Restaurant).all()

'''should see something like [database_setup.Restaurant object at 07xxxx]
add menu item
'''

''''cheesepizza = MenuItem(name = "Cheesier Pizza",
 description = "Made with all natural ingredients and fresh mozzarella",
 course = "Entree",
 price = "$8.99",
 restaurant = myFirstRestaurant)
session.add(cheesepizza)
session.commit()'''

session.query(MenuItem).all()