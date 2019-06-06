#!/usr/bin/env python
from flask import Flask, render_template, request
from flask import redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy.orm.exc import NoResultFound
from database_setup import Base, Item, Category, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


app = Flask(__name__)
#Connect to Database and create database session
engine = create_engine('sqlite:///itemcatalog.db', connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
#APPLICATION = "Restaurant Menu App"

# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state

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
        response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
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
        return response

     # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user already connected'),
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

    login_session['username'] = data['name'] #email?
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists , if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' "style = "width: 300px; height: 300px;border-radius: 150px;'\
        '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("Welcome, %s" % login_session['username'])
    print "done!"
    return output

def createUser(login_session):
    """
      Function to to create user from google connect
      Args:
        login_session
      Return:
        user id
    """
    newUser = User(
        name=login_session['username'],
        email=login_session['email'],
        picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

def getUserInfo(user_id):
    """
      Function to to get user information from database
      Args:
        user_id
      Return:
        user details
    """
    user = session.query(User).filter_by(id=user_id).one()
    return user

def getUserID(email):
    """
      Function to to get user details through email from database
      Args:
        email
      Return:
        user id
    """
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except BaseException:
        return None

    # DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    """
      Function to disconnect from google acccount
    """
    access_token = login_session['access_token']
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: %s' % login_session['username']
    if access_token is None:
        response = make_response(json.dumps('Current user not connected.'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']   # noqa
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("Successfully disconnected.")
        return redirect(url_for('catalogFunction'))
        # return response
    else:

        response = make_response(
            json.dumps(
                'Failed to revoke token for given user.',
                400))
        response.headers['Content-Type'] = 'application/json'
        return response

@app.route('/category/JSON')
def categoriesJSON():
    category = session.query(Category)
    items = session.query(Item).filter_by(category_id=Item.category_id).all()
    return jsonify(Categories= [i.serialize for i in category], Items=[i.serialize for i in items])


#JSON APIs to view Restaurant Information
@app.route('/category/<int:category_id>/items/JSON')
def categoriesItemsJSON(category_id):
    category2 = session.query(Category).filter_by(id = category_id).one()
    items = session.query(Item).filter_by(category_id = category_id).all()
    return jsonify(Items=[i.serialize for i in items])


@app.route('/category/<int:category_id>/items/<int:item_id>/JSON')
def itemJSON(category_id, item_id):
    items = session.query(Item).filter_by(id = item_id).one()
    return jsonify(Items = items.serialize)




#Show all restaurants
@app.route('/')
@app.route('/category/')
def catalogFunction():
    flash("Hello")
    category = session.query(Category)
    items = session.query(Item).filter_by(category_id=Item.category_id).order_by(Item.id.desc()).limit(8).all()
    if 'username' not in login_session:
        if category.count() == 0:
            flash("No categories yet")
            return render_template('publicCatalog.html', m_instruments=category, itemName=items)
        else:
            return render_template('publicCatalog.html', m_instruments=category, itemName=items)
    else:
        if category.count() == 0:
            flash("No categories yet")
            return render_template('catalog.html', m_instruments=category, itemName=items)
        else:
            flash("Hello")
            return render_template('catalog.html', m_instruments=category, itemName=items)


#Create a new restaurant
@app.route('/category/new/', methods=['GET','POST'])
def newCategoryFunction():
    category = session.query(Category)
    # Check if user is logged. If not, redirect to login page
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newCategory = Category(name = request.form['name'], user_id=login_session['user_id'])
        session.add(newCategory)

        session.commit()
        flash('New Category %s Successfully Created' % newCategory.name)
        return redirect(url_for('catalogFunction', category=category))
    else:
        return render_template('newCategory.html', category=category)

@app.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
def editCategoryFunction(category_id):
    category2 = session.query(Category).filter_by(id=category_id).first()
    # Check if the inserted category id exist in db
    if not hasattr(category2, 'id'):
        return "this category not exist"
    # Check if user is logged. If not, redirect to login page
    if 'username' not in login_session:
        return redirect('/login')
    if category2.user_id != login_session['user_id']:
        flash("You not authorizated to edit this category.")
        return redirect(url_for('catalogFunction'))
    # Receive edited category name from the editCategory page
    if request.method == 'POST':
        if request.form['name']:
            category2.name = request.form['name']
        session.add(category2)
        session.commit()
        flash("The category was seccessfully edited!")
        return redirect(url_for('catalogFunction', category2=category2))
    else:
        return render_template('editCategory.html', category2=category2)



#Delete a restaurant
@app.route('/category/<int:category_id>/delete/', methods = ['GET','POST'])
def deleteCategoryFunction(category_id):
  category = session.query(Category)
  category2 = session.query(Category).filter_by(id = category_id).first()
  #deleteItem = session.query(Item).filter_by(category_id = category2.id).delete()
  if not hasattr(category2, 'id'):
      return "this category does not exist"
  if 'username' not in login_session:
      return redirect('/login')
  if login_session['user_id'] != category2.user_id:
      flash ("Sorry, you cannot delete this category.")
      return redirect(url_for('catalogFunction'))
  if request.method == 'POST':
      session.delete(category2)
      session.commit()
      flash('%s Successfully Deleted' % category2.name)
      return redirect(url_for('catalogFunction', m_instruments = category))
  else:
      return render_template('deleteCategory.html',category2 = category2)

# Create route to display the items for the selected category
@app.route('/category/<int:category_id>/items')
def categoryFunction(category_id):
    category = session.query(Category)
    category2 = session.query(Category).filter_by(id=category_id).first()
    # Check if the inserted category id exist in db
    if not hasattr(category2, 'id'):
        return "this category not exist"
    items = session.query(Item).filter_by(category_id=category2.id)
    flash("dfgcategory")

    # Check if user is logged. If not, display the public page
    if 'username' not in login_session:
        # Check if have items in db
        if items.count() == 0:
            flash("You have no items yet!")
            return render_template(
                'publicCategory.html',
                m_instruments=category, m_instruments2=category2, itemName=items)
        else:
            return render_template(
                'publicCategory.html',
                m_instruments=category, m_instruments2=category2, itemName=items)
    # If logged user, display the logged users page
    else:
        # Check if have items in db
        if items.count() == 0:
            flash("You have no items yet!")
            return render_template(
                'category.html',
                m_instruments=category, m_instruments2=category2, itemName=items)
        else:
            return render_template(
                'category.html',
                m_instruments=category, m_instruments2=category2, itemName=items)
#Show a restaurant menu
# Create the app.route function to display item
@app.route('/category/<int:category_id>/items/<int:item_id>')
def itemFunction(category_id, item_id):
    category2 = session.query(Category).filter_by(id=category_id).first()
    # Check if the inserted category id exist in db
    if not hasattr(category2, 'id'):
        return "this category not exist"
    items = session.query(Item).filter_by(id=item_id).first()
    # Check if the inserted items id exist in db
    if not hasattr(items, 'id'):
        return "this item not exist"
    # check if iserted item_id has the same iserted category_id as atribute
    if items.category_id != category_id:
        return "This item not exist in this category"
    # Check if user is logged. If not, redirect to the login page
    if 'username' not in login_session:
        return render_template(
            'publicItem.html', itemName=items, category=category2)
    else:
        return render_template('item.html', itemName=items, category=category2)



#Create a new menu item
@app.route('/category/<int:category_id>/items/new/',methods=['GET','POST'])
def newItemFunction(category_id):
  category = session.query(Category)
  category2 = session.query(Category).filter_by(id = category_id).first()
  if not hasattr(category2, 'id'):
      return "this category does not exist"
  if 'username' not in login_session:
      return redirect('/login')

  if request.method == 'POST':
      newItem = Item(name = request.form['name'], description = request.form['description'], category_id=request.form['category'], user_id=login_session['user_id'])
      session.add(newItem)
      session.commit()
      flash('New %s Item Successfully Created' % (newItem.name))
      return redirect(url_for('categoryFunction', category_id = newItem.category_id))
  else:
      return render_template('newItem.html', category=category, category2=category2)

#Edit a menu item
@app.route('/category/<int:category_id>/items/<int:item_id>/edit', methods=['GET','POST'])
def editItemFunction(category_id, item_id):

    category = session.query(Category)
    category2 = session.query(Category).filter_by(id = category_id).first()
    if not hasattr(category2, 'id'):
        return "this category not exist"
    editItem = session.query(Item).filter_by(id=item_id).first()
    # Check if the inserted items id exist in db
    if not hasattr(editItem, 'id'):
        return "this item not exist"
    # check if iserted item_id has the same iserted category_id as atribute
    if editItem.category_id != category_id:
        return "This item not exist in this category"
    # Check if user is logged. If not, redirect to the login page
    if 'username' not in login_session:
        return redirect('/login')
    # Check if the logged user is the creator of the item. If not, display
    # an authorization error message
    if login_session['user_id'] != editItem.user_id:
        flash("You not authorizated to edit this item.")
        return redirect(url_for('catalogFunction'))

    if request.method == 'POST':
        if request.form['name']:
            editItem.name = request.form['name']
        if request.form['description']:
            editItem.description = request.form['description']
        if request.form['category']:
            editItem.category_id = request.form['category']

        session.add(editItem)
        session.commit()
        flash(' Item Successfully Edited')
        return redirect(url_for('itemFunction', category_id=editItem.category_id, item_id=item_id))
    else:
        return render_template('editItem.html', category=category, category2=category2, editItem=editItem)


#Delete a menu item
@app.route('/category/<int:category_id>/items/<int:item_id>/delete', methods = ['GET','POST'])
def deleteItemFunction(category_id, item_id):
    category2 = session.query(Category).filter_by(id = category_id).first()

    if not hasattr(category2, 'id'):
        return "this category not exist"
    deleteItem = session.query(Item).filter_by(id=item_id).first()
    # Check if the inserted items id exist in db
    if not hasattr(deleteItem, 'id'):
        return "this item not exist"
    # check if iserted item_id has the same iserted category_id as atribute
    if deleteItem.category_id != category_id:
        return "This item not exist in this category"
    # Check if user is logged. If not, redirect to the login page
    if 'username' not in login_session:
        return redirect('/login')
    # Check if the logged user is the creator of the item. If not, display
    # an authorization error message
    if login_session['user_id'] != deleteItem.user_id:
        flash("You not authorizated to delete this item.")
        return redirect(url_for('catalogFunction'))
    if request.method == 'POST':
        session.delete(deleteItem)
        session.commit()
        flash(' Item Successfully Deleted')
        return redirect(url_for('categoryFunction', category_id=category2.id))
    else:
        return render_template('deleteItem.html', category_id=category_id, item = deleteItem)




if __name__ == '__main__':
  app.secret_key = 'super_secret_key'
  app.debug = True
  app.run(host = '0.0.0.0', port = 5000)
