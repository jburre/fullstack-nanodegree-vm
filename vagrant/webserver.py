from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Restaurant, Base

engine=create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind=engine
DBSession=sessionmaker(bind=engine)
session=DBSession()



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
                output += "<html><body>"
                output += "<h1>&#161 Hola !</h1>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/hello'><h3>What would you like me to say?</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

## do the restaurants listings
            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output=""
                output+="<html><body><h1>All our restaurants</h1>"
                output+='<a href="/restaurants/new">Make a new restaurant here</a><br/>'
                for entry in session.query(Restaurant).all():
                    output+="<h2>"
                    output+=entry.name
                    output+="</h2>"
                    output+="<a href='restaurants/%s/edit'>Edit</a><br/>" % entry.id
                    output+="<a href='restaurants/%s/delete'>Delete</a><br/>" % entry.id
                    print entry
                output+="</body></html>"
                self.wfile.write(output)
                print output
                return

## new restaurants needs the land
            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()
                output=""
                output+="<html><body>"
                output+="<h1>Make a new Restaurant</h1><br/>"
                output+='''<form method='POST' enctype='multipart/form-data' action='/restaurants/new'><input name="newRestaurantName" type="text" placeholder='New Restaurant Name'><input type="submit" value="Create"></form>"'''
                output+="</body></html>"
                self.wfile.write(output)
                print output
                return

## another name, if you wish so
            if self.path.endswith("/edit"):
                restaurantIDPath= self.path.split("/")[2]
                restaurantQuery=session.query(Restaurant).filter_by(id =restaurantIDPath).one()
                if restaurantQuery:
                    self.send_response(200)
                    self.send_header('Content-type','text/html')
                    self.end_headers()
                    output=""
                    output+="<html><body>"
                    output+="<h1>"
                    output+=restaurantQuery.name
                    output+="</h1>"
                    output+="<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/edit'>" % restaurantIDPath
                    output+="<input name='newName' type='text' placeholder='%s'><input type='submit' value='Update'></form>" % restaurantQuery.name
                    ##output+=self.path[-6:-5] #just for debugging purpose
                    output+="</body></html>"
                    self.wfile.write(output)

###Time to say goodbye dear Restaurant
            if self.path.endswith("/delete"):
                restaurantIDPath=self.path.split("/")[2]
                restaurantQuery=session.query(Restaurant).filter_by(id=restaurantIDPath).one()
                if restaurantQuery:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output=""
                    output+="<html><body><h1>Are you sure you want to delete "
                    output+=restaurantQuery.name
                    output+="</h1>"
                    output+="<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/delete'>" % restaurantIDPath
                    output+="<input type ='submit' value ='Delete'></form>"
                    output+="</body></html>"
                    self.wfile.write(output)

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        try:
            if (self.path.endswith("/hello")) or (self.path.endswith("/hola")):
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('message')
                output = ""
                output += "<html><body>"
                output += " <h2> Okay, how about this: </h2>"
                output += "<h1> %s </h1>" % messagecontent[0]
                output += '''<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
                output += "</body></html>"
                self.wfile.write(output)
                print output

            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(
                        self.headers.getheader('content-type'))
                if ctype=='multipart/form-data':
                    fields=cgi.parse_multipart(self.rfile, pdict)
                    messagecontent=fields.get('newRestaurantName')
                    newRestaurant=Restaurant(name=messagecontent[0])
                    session.add(newRestaurant)
                    session.commit()
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()
            ## what about a new name for a Restaurant
            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(
                        self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent=fields.get('newName')
                    print messagecontent[0]
                    restaurantIDPath=self.path.split("/")[2]
                    print restaurantIDPath
                    myRestaurantQuery=session.query(Restaurant).filter_by(id=restaurantIDPath).one()
                    print myRestaurantQuery.name
                    if myRestaurantQuery != []:
                        myRestaurantQuery.name = messagecontent[0]
                        session.add(myRestaurantQuery)
                        session.commit()
                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Location','/restaurants')
                        self.end_headers()

            if self.path.endswith("/delete"):
                restaurantIDPath=self.path.split("/")[2]
                myRestaurantQuery=session.query(Restaurant).filter_by(id=restaurantIDPath).one()
                session.delete(myRestaurantQuery)
                session.commit()
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()
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
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
