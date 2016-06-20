from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from music_db_setup import Base, Playlist, Song, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Custom Playlists"


# Connect to Database and create database session
engine = create_engine('sqlite:///playlists.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None



# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)



@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# JSON API to view Restaurant Information
@app.route('/playlist/JSON')
def playlistsJSON():
    playlists = session.query(Playlist).all()
    return jsonify(playlists=[p.serialize for p in playlists])

# JSON API to view songs in a playlist
@app.route('/playlist/<int:playlist_id>/songs_in_playlist/JSON')
def playlistSongsJSON(playlist_id):
    playlist = session.query(Playlist).filter_by(id=playlist_id).one()
    items = session.query(Song).filter_by(
        playlist_id=playlist_id).all()
    return jsonify(Songs=[i.serialize for i in items])

# JSON API to view all songs
@app.route('/playlist/all_songs/JSON')
def allSongsJSON():
    songs = session.query(Song).all()
    return jsonify(songs=[s.serialize for s in songs])


# Show all playlists
@app.route('/')
@app.route('/playlist/')
def showPlaylists():
    playlists = session.query(Playlist).order_by(asc(Playlist.title))
    songs = session.query(Song).order_by(desc(Song.id)).limit(2)
    if 'username' not in login_session:
        return render_template('public_playlists.html', playlists=playlists)
    else:
        return render_template('playlist.html', playlists=playlists, items = songs)

@app.route('/playlist/new/', methods=['GET', 'POST'])
def newPlaylist():
    #if 'username' not in login_session:
     #   return redirect('/login')
    if request.method == 'POST':
        newPlaylist = Playlist(title=request.form['title'])#, user_id=login_session['user_id'])
        session.add(newPlaylist)
        flash('New Playlist %s Successfully Created' % newPlaylist.title)
        session.commit()
        return redirect(url_for('showPlaylists'))
    else:
        return render_template('new_playlist.html')

@app.route('/playlist/<int:playlist_id>/')
@app.route('/playlist/<int:playlist_id>/songs/')
def showSongs(playlist_id):
    playlist = session.query(Playlist).filter_by(id=playlist_id).one()
    creator = getUserInfo(playlist.user_id)
    items = session.query(Song).filter_by(
        playlist_id=playlist_id).all()
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('public_list_of_songs.html', items=items, playlist=playlist, creator=creator)
    else:
        return render_template('list_of_songs.html', items=items, playlist=playlist)

@app.route('/playlist/<int:playlist_id>/edit/', methods=['GET', 'POST'])
def editPlaylist(playlist_id):
    editedPlaylist = session.query(
        Playlist).filter_by(id=playlist_id).one()
    #if 'username' not in login_session:
     #   return redirect('/login')
    #if editedRestaurant.user_id != login_session['user_id']:
    #    return "<script>function myFunction() {alert('You are not authorized to edit this restaurant. Please create your own restaurant in order to edit.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['title']:
            editedPlaylist.title = request.form['title']
            editedPlaylist.description = request.form['description']
            session.commit()
            flash('Playlist Successfully Edited %s' % editedPlaylist.title)
            return redirect(url_for('showPlaylists'))
    else:
        return render_template('edit_playlist.html', playlist=editedPlaylist)

# Create a new menu item
@app.route('/playlist/<int:playlist_id>/song/new/', methods=['GET', 'POST'])
def newSong(playlist_id):
    #if 'username' not in login_session:
     #   return redirect('/login')
    playlist = session.query(Playlist).filter_by(id=playlist_id).one()
    #if login_session['user_id'] != restaurant.user_id:
        #return "<script>function myFunction() {alert('You are not authorized to add menu items to this restaurant. Please create your own restaurant in order to add items.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        newSong = Song(title=request.form['title'], performed_by=request.form['performed_by'], album=request.form[
                               'album'], notes=request.form['notes'], playlist_id=playlist_id, user_id=playlist.user_id)
        session.add(newSong)
        session.commit()
        flash('New Song %s Item Successfully Created' % (newSong.title))
        return redirect(url_for('showSongs', playlist_id=playlist_id))
    else:
        return render_template('new_song.html', playlist_id=playlist_id)

# Delete a playlist
@app.route('/playlist/<int:playlist_id>/delete/', methods=['GET', 'POST'])
def deletePlaylist(playlist_id):
    playlistToDelete = session.query(
        Playlist).filter_by(id=playlist_id).one()
    songsToDelete = session.query(Song).filter_by(playlist_id = playlist_id).all()
    #if 'username' not in login_session:
     #   return redirect('/login')
    #if restaurantToDelete.user_id != login_session['user_id']:
     #   return "<script>function myFunction() {alert('You are not authorized to delete this restaurant. Please create your own restaurant in order to delete.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(playlistToDelete)
        flash('%s Successfully Deleted' % playlistToDelete.title)
        session.commit()
        return redirect(url_for('showPlaylists', playlist_id=playlist_id))
    else:
        return render_template('delete_playlist.html', playlist=playlistToDelete)

# Delete a song
@app.route('/playlist/<int:playlist_id>/song/<int:song_id>/edit', methods=['GET', 'POST'])
def editSong(playlist_id, song_id):
    #if 'username' not in login_session:
     #   return redirect('/login')
    editedSong = session.query(Song).filter_by(id=song_id).one()
    playlist = session.query(Playlist).filter_by(id=playlist_id).one()
    #if login_session['user_id'] != restaurant.user_id:
     #   return "<script>function myFunction() {alert('You are not authorized to edit menu items to this restaurant. Please create your own restaurant in order to edit items.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['title']:
            editedSong.title = request.form['title']
        if request.form['performed_by']:
            editedSong.performed_by = request.form['performed_by']
        if request.form['album']:
            editedSong.album = request.form['album']
        if request.form['notes']:
            editedSong.notes = request.form['notes']
        session.add(editedSong)
        session.commit()
        flash('Song Successfully Edited')
        return redirect(url_for('showSongs', playlist_id=playlist_id))
    else:
        return render_template('edit_song.html', playlist_id=playlist_id, song_id=song_id, item=editedSong)

# Delete a menu item
@app.route('/playlist/<int:playlist_id>/song/<int:song_id>/delete', methods=['GET', 'POST'])
def deleteSong(playlist_id, song_id):
    #if 'username' not in login_session:
     #   return redirect('/login')
    playlist = session.query(Playlist).filter_by(id=playlist_id).one()
    songToDelete = session.query(Song).filter_by(id=song_id).one()
    #if login_session['user_id'] != restaurant.user_id:
     #   return "<script>function myFunction() {alert('You are not authorized to delete menu items to this restaurant. Please create your own restaurant in order to delete items.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(songToDelete)
        session.commit()
        flash('Song Successfully Deleted')
        return redirect(url_for('showSongs', playlist_id=playlist_id))
    else:
        return render_template('delete_song.html', item=songToDelete, playlist_id = playlist_id)
 

'''

# DISCONNECT - Revoke a current user's token and reset their login_session



# JSON APIs to view Restaurant Information
@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(
        restaurant_id=restaurant_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(restaurant_id, menu_id):
    Menu_Item = session.query(MenuItem).filter_by(id=menu_id).one()
    return jsonify(Menu_Item=Menu_Item.serialize)


@app.route('/restaurant/JSON')
def restaurantsJSON():
    restaurants = session.query(Restaurant).all()
    return jsonify(restaurants=[r.serialize for r in restaurants])


# Show all restaurants
@app.route('/')
@app.route('/restaurant/')
def showRestaurants():
    restaurants = session.query(Restaurant).order_by(asc(Restaurant.name))
    if 'username' not in login_session:
        return render_template('publicrestaurants.html', restaurants=restaurants)
    else:
        return render_template('restaurants.html', restaurants=restaurants)

# Create a new restaurant


@app.route('/restaurant/new/', methods=['GET', 'POST'])
def newRestaurant():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newRestaurant = Restaurant(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(newRestaurant)
        flash('New Restaurant %s Successfully Created' % newRestaurant.name)
        session.commit()
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('newRestaurant.html')

# Edit a restaurant


@app.route('/restaurant/<int:restaurant_id>/edit/', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
    editedRestaurant = session.query(
        Restaurant).filter_by(id=restaurant_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedRestaurant.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this restaurant. Please create your own restaurant in order to edit.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            editedRestaurant.name = request.form['name']
            flash('Restaurant Successfully Edited %s' % editedRestaurant.name)
            return redirect(url_for('showRestaurants'))
    else:
        return render_template('editRestaurant.html', restaurant=editedRestaurant)


# Delete a restaurant
@app.route('/restaurant/<int:restaurant_id>/delete/', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    restaurantToDelete = session.query(
        Restaurant).filter_by(id=restaurant_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if restaurantToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete this restaurant. Please create your own restaurant in order to delete.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(restaurantToDelete)
        flash('%s Successfully Deleted' % restaurantToDelete.name)
        session.commit()
        return redirect(url_for('showRestaurants', restaurant_id=restaurant_id))
    else:
        return render_template('deleteRestaurant.html', restaurant=restaurantToDelete)

# Show a restaurant menu


@app.route('/restaurant/<int:restaurant_id>/')
@app.route('/restaurant/<int:restaurant_id>/menu/')
def showMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    creator = getUserInfo(restaurant.user_id)
    items = session.query(MenuItem).filter_by(
        restaurant_id=restaurant_id).all()
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('publicmenu.html', items=items, restaurant=restaurant, creator=creator)
    else:
        return render_template('menu.html', items=items, restaurant=restaurant, creator=creator)


# Create a new menu item
@app.route('/restaurant/<int:restaurant_id>/menu/new/', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    if 'username' not in login_session:
        return redirect('/login')
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if login_session['user_id'] != restaurant.user_id:
        return "<script>function myFunction() {alert('You are not authorized to add menu items to this restaurant. Please create your own restaurant in order to add items.');}</script><body onload='myFunction()''>"
        if request.method == 'POST':
            newItem = MenuItem(name=request.form['name'], description=request.form['description'], price=request.form[
                               'price'], course=request.form['course'], restaurant_id=restaurant_id, user_id=restaurant.user_id)
            session.add(newItem)
            session.commit()
            flash('New Menu %s Item Successfully Created' % (newItem.name))
            return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('newmenuitem.html', restaurant_id=restaurant_id)

# Edit a menu item


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit', methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(MenuItem).filter_by(id=menu_id).one()
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if login_session['user_id'] != restaurant.user_id:
        return "<script>function myFunction() {alert('You are not authorized to edit menu items to this restaurant. Please create your own restaurant in order to edit items.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['price']:
            editedItem.price = request.form['price']
        if request.form['course']:
            editedItem.course = request.form['course']
        session.add(editedItem)
        session.commit()
        flash('Menu Item Successfully Edited')
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('editmenuitem.html', restaurant_id=restaurant_id, menu_id=menu_id, item=editedItem)


# Delete a menu item
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete', methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    if 'username' not in login_session:
        return redirect('/login')
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    itemToDelete = session.query(MenuItem).filter_by(id=menu_id).one()
    if login_session['user_id'] != restaurant.user_id:
        return "<script>function myFunction() {alert('You are not authorized to delete menu items to this restaurant. Please create your own restaurant in order to delete items.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Menu Item Successfully Deleted')
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('deleteMenuItem.html', item=itemToDelete)


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            credentials = login_session.get('credentials')
            del credentials
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showRestaurants'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showRestaurants'))

'''
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)