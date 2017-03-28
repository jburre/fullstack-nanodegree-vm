from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Restaurant, MenuItem, Base

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind=engine
DBSession=sessionmaker(bind=engine)
session=DBSession()

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
        newItem=MenuItem(name=request.form['name'], restaurant_id=restaurant_id)
        session.add(newItem)
        session.commit()
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete', methods=['GET','POST'])
def deleteMenuItem(restaurant_id, menu_id):
    toDelete=session.query(MenuItem).filter_by(id=menu_id).one()
    print toDelete.name
    if request.method=="GET":
        return render_template('deletemenuitem.html', restaurant_id=restaurant_id, menu_id=menu_id, item=toDelete)
    else:
        session.delete(menu_item)
        session.commit()
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))


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
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))

@app.route('/')
def Restaurants():
    restaurants=session.query(Restaurant).all()
    return printMain(restaurants)

def printMain(restaurants):
    return render_template('index.html', restaurants=restaurants)

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
    
