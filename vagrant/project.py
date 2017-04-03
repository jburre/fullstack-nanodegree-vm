from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Restaurant, MenuItem, Base

# new steps for Auth
# since session is already used, use new name
from flask import session as login_session
import random, string 

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind=engine
DBSession=sessionmaker(bind=engine)
session=DBSession()


#new route for login
#create state token
@app.route("/login")
def showLogin():
    state=''.join(random.choice(string.ascii_letters+string.digits) for x in xrange(32))
    login_session['state']=state
    return "The current session state is %s" %login_session['state']

#making an API endpoint (just GET for now)
@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def restaurantMenuJson(restaurant_id):
    restaurant=session.query(Restaurant).filter_by(id=restaurant_id).one()
    items=session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])

@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(restaurant_id, menu_id):
    Menu_item=session.query(MenuItem).filter_by(id=menu_id).one()
    return jsonify(Menu_item=Menu_Item.serialize)

@app.route('/restaurants/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
    restaurant=session.query(Restaurant).filter_by(id=restaurant_id).one()
    items=session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
    return render_template('menu.html', restaurant=restaurant, items=items)

@app.route('/restaurants/<int:restaurant_id>/new', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    if request.method == 'GET':
        return render_template('newmenuitem.html', restaurant_id=restaurant_id)
    else:
        if request.form['name'] and request.form['price'] and request.form['description']:
            newItem=MenuItem(name=request.form['name'], restaurant_id=restaurant_id)
            newItem.price=request.form['price']
            newItem.description=request.form['description']
            session.add(newItem)
            session.commit()
            flash("new menu item created!")
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete', methods=['GET','POST'])
def deleteMenuItem(restaurant_id, menu_id):
    toDelete=session.query(MenuItem).filter_by(id=menu_id).one()
    print toDelete.name
    if request.method=="GET":
        return render_template('deletemenuitem.html', restaurant_id=restaurant_id, menu_id=menu_id, item=toDelete)
    else:
        session.delete(toDelete)
        session.commit()
        flash("an item was deleted")
        return render_template('deleteConfirmation.html', item=toDelete, restaurant_id=restaurant_id)

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit', methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    menu_Item=session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method=='GET':
        return render_template('editmenuitem.html', restaurant_id=restaurant_id, menu_id=menu_id, item=menu_Item)
    else:
        if request.form['newName']:
            menu_Item.name=request.form['newName']
        session.add(menu_Item)
        session.commit()
        flash("an item was edited sucessfully")
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))

@app.route('/')
def Restaurants():
    restaurants=session.query(Restaurant).all()
    return printMain(restaurants)

def printMain(restaurants):
    return render_template('index.html', restaurants=restaurants)

if __name__ == '__main__':
    app.secret_key='super_secret_key' #yeah, thanks that our app is not live
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
    
