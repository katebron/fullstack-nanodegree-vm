from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from urlparse import urlparse, urldefrag
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

#Create session and connect to DB
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()


class webServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith("/restaurant"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                places = session.query(Restaurant).all()
                start = ""
                start += "<html><body>"
                start += "<h1>List of restaurants</h1>"
                start += "<p>" 

                #output += '''<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
                
                self.wfile.write(start)
                end = ""
                end += "<a href='/new'>Add a new restaurant</a>"
                end += "</body></html>"
                print start
                for place in places: 
                    output = place.name 
                    output += " <a href ='/restaurants/%s/edit' >Edit </a>  " % place.id
                    output += " <a href='/restaurants/%s/delete'>Delete</a> </br>" %place.id           
                    print output
                    self.wfile.write(output)
                self.wfile.write(end)
                print end
                return

            if self.path.endswith("/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>Add a</h1>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/new'><p>Add a new restaurant</p><input name="newrestaurant" type="text" ><input type="submit" value="Submit"> </form>'''
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/edit"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                #url, fragment = urldefrag(self.path)
                rid = self.path.split("/")[2]
                #rid = fragment
                place = session.query(Restaurant).filter_by(id=rid).one()
                output = ""
                output += "<html><body>"
                output += "This is the id: %s" % rid
                output += "<h1>Edit this name: "
                output += place.name
                output += " </h1>"
                output += "<form method='POST' enctype='multipart/form-data' action='restaurants/%s/edit'>" %place.id
                output += "<p>Edit this restaurant's name</p><input id = '"
                output += "' name='editrestaurant' type='text' ><input type='submit' value='Submit'> </form>"
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return   

            if self.path.endswith("/delete"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                #url, fragment = urldefrag(self.path)
                rid = self.path.split("/")[2]
                #rid = fragment
                place = session.query(Restaurant).filter_by(id=rid).one()
                output = ""
                output += "<html><body>"
                output += "This is the id: %s" % rid
                output += "<h1>Delete this restaurant: "
                output += place.name
                output += " </h1>"
                output += "<form method='POST' enctype='multipart/form-data' action='restaurants/%s/delete'>" %place.id
                output += "<p>Are you sure you want to delete this restaurant?</p><input type='submit' value='Yes, Delete'> </form>"
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return     
        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        try:          
            '''self.send_response(301)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            '''
            if self.path.endswith("/new"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newrestaurant')
                    #session = DBSession()
                    restaurant = Restaurant(name = messagecontent[0])
                    session.add(restaurant)
                    session.commit()
            
            if self.path.endswith("?id="):  
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type')) 
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newrestaurant')
                    #session = DBSession()
                    restaurant = Restaurant(name = messagecontent[0])
                    session.add(restaurant)
                    session.commit()       
            
            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('editrestaurant')
                    #session = DBSession()

                    #newName = Restaurant(name = messagecontent[0])
                    newName = messagecontent[0]
                    rid = self.path.split("/")[2]
                    restaurantQ = session.query(Restaurant).filter_by(id=rid).one()
                    if newName != "":
                        restaurantQ.name = newName
                        session.add(restaurantQ)
                        session.commit()

            if self.path.endswith("/delete"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    rid = self.path.split("/")[2]
                    deleteR = session.query(Restaurant).filter_by(id=rid).one()
                    session.delete(deleteR)
                    session.commit()

            self.send_response(301)
            self.send_header('Content-type', 'text/html')
            self.send_header('Location', '/restaurant')
            self.end_headers()
            print output
        except:
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webServerHandler)
        print "Web Server running on port %s" % port
        server.serve_forever()
    except KeyboardInterrupt:
        print " ^C entered, stopping web server...."
        server.socket.close()

if __name__ == '__main__':
    main()
