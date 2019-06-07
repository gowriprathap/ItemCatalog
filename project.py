#!/usr/bin/env python
from flask import Flask, render_template, request
# importing modules from Flask
from flask import redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
# importing modules from sqlalchemy
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy.orm.exc import NoResultFound
from database_setup import Base, Item, Category, User
# Importing the tables from database_setup
# the python program which created the database
from flask import session as login_session
# modules to know if user is signed in or not
import random
import string
from oauth2client.client import flow_from_clientsecrets
# importing modules for google sign in button
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
# importing json
import json
from flask import make_response
import requests


app = Flask(__name__)
# Connect to Database and create database session
engine = create_engine('sqlite:///itemcatalog.db',
                       connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# storing the client id from the json file for google login
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']


# Create anti-forgery state token
@app.route('/login')
# for URL ending with /login, which is the page when user logs in using google
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    # making a random state
    # to reduce the probability of attack from malicious users
    login_session['state'] = state
    # storing the state in a variable for later use

    return render_template('login.html', STATE=state)
    # using the login.html file to display


@app.route('/gconnect', methods=['POST'])
# routing function that accepts post requests
# using google to sign into the application
def gconnect():

    # Validate state token and see if the token the client
    # sent the server matches the token the server sent to the client
    # To protect from malicious users
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data
    try:
        # Using one time code and exchanging it for a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'  # the one time code
        credentials = oauth_flow.step2_exchange(code)
        # initiating the exchange by passing in the one time code
    except FlowExchangeError:
        # if an error happens, send the response as a JSON object
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    # Google API server will verify that this is a valid token for use
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info,
    # send a 500 internal server error to the client
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # If they do not match, then send a 401 response using JSON
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        # print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    # If the user is already logged in,
    # a 200 successful message is given without resetting all the variables.
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user already connected'),
                                 200)
        # The user is already connected
        response.headers['Content-Type'] = 'application/json'
        return response

    # If none of the if statements were true,
    # the user successfully logged in
    # and these variables are stored for use later.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    # obtaining the user name from google log in
    login_session['picture'] = data['picture']
    # obtaining the picture from google log in
    login_session['email'] = data['email']
    # obtaining the email from google log in

    # if te user doesn't exist, make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id  # obtain the user id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' "style = "width: 300px; height: 300px;border-radius: 150px;'\
        '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("Welcome to the Catalog, %s" % login_session['username'])

    return output


def createUser(login_session):  # Function to create user from google connect
    # Argument is login_session
    # Return is user id

    newUser = User(
        name=login_session['username'],
        email=login_session['email'],
        picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):  # Function to get user information from database
    # Argument is user_id
    # Return is user details

    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):  # Function for user details through email from database
    # Argument is email
    # Return is user id

    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except BaseException:
        return None


# DISCONNECT - Log out a user
@app.route('/gdisconnect')
def gdisconnect():  # Function to disconnect from the google account

    access_token = login_session['access_token']
    if access_token is None:
        response = make_response(json.dumps('Current user not connected.'),
                                 401)
        # The user was not logged in
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        del login_session['access_token']  # deleting the access token
        del login_session['gplus_id']
        del login_session['username']
        # deleting all the details and reseeting so that the user can log out
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("You have successfully logged out.")
        # Flashing a message when logged out
        return redirect(url_for('catalogFunction'))
        # returning to original page
        # return response
    else:

        response = make_response(
            json.dumps(
                'Failed to revoke token for given user.',
                400))
        # if the server is not able to retrieve
        # the token to log the user out
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/category/JSON')  # URL with category
def categoriesJSON():
    category = session.query(Category)
    items = session.query(Item).filter_by(category_id=Item.category_id).all()
    return jsonify(Categories=[
        i.serialize for i in category], Items=[i.serialize for i in items])


# JSON APIs to view Category Information
@app.route('/category/<int:category_id>/items/JSON')
def categoriesItemsJSON(category_id):
    category2 = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category_id).all()
    return jsonify(Items=[i.serialize for i in items])


@app.route('/category/<int:category_id>/items/<int:item_id>/JSON')
def itemJSON(category_id, item_id):
    items = session.query(Item).filter_by(id=item_id).one()
    return jsonify(Items=items.serialize)


# Show all categories
@app.route('/')
@app.route('/category/')
def catalogFunction():

    category = session.query(Category)
    items = session.query(Item).filter_by(
        category_id=Item.category_id).order_by(Item.id.desc()).limit(8).all()
    if 'username' not in login_session:  # If the user is not logged in
        if category.count() == 0:  # If there are not categories
            flash("There are no categories yet")
            return render_template(
                'publicCatalog.html', m_instruments=category, itemName=items)
        else:
            return render_template(
                'publicCatalog.html', m_instruments=category, itemName=items)
    else:
        if category.count() == 0:
            # The user is logged in, and there are no categories
            flash("No categories yet")
            return render_template(
                'catalog.html', m_instruments=category, itemName=items)
        else:

            return render_template(
                'catalog.html', m_instruments=category, itemName=items)


# Create a new category
@app.route('/category/new/', methods=['GET', 'POST'])
def newCategoryFunction():
    category = session.query(Category)
    # Check if user is logged. If not, redirect to login page
    if 'username' not in login_session:
        # if the user is not logged in, then redirecting to the login page
        return redirect('/login')
    if request.method == 'POST':
        newCategory = Category(
            name=request.form['name'], user_id=login_session['user_id'])
        # Taking in information from the user
        session.add(newCategory)

        session.commit()
        flash('The new Category %s is successfully Created' % newCategory.name)
        # Flashing the message that the new category was created
        return redirect(url_for('catalogFunction', category=category))
        # Redirecting to the catalog page
    else:
        return render_template('newCategory.html', category=category)


@app.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
# To edit a category
def editCategoryFunction(category_id):
    category2 = session.query(Category).filter_by(id=category_id).first()
    # Check if the inserted category id exist in database
    if not hasattr(category2, 'id'):
        return "this category not exist"
    # Check if user is logged. If not, redirect to login page
    if 'username' not in login_session:
        # If the user is not logged in, redirect to the login page
        return redirect('/login')
    if category2.user_id != login_session['user_id']:
        # If the user who created the category
        # is not the one who is logged in now
        flash("Sorry, you not authorized to edit this category.")
        # That person is not authorized to edit
        return redirect(url_for('catalogFunction'))
    # Receive edited category name
    if request.method == 'POST':
        if request.form['name']:
            category2.name = request.form['name']
        session.add(category2)
        session.commit()
        # Committing to the session to save changes
        flash("The category was successfully edited.")
        # Flashing a message to show that the cateogry was successfully edited
        return redirect(url_for('catalogFunction', category2=category2))
    else:
        return render_template('editCategory.html', category2=category2)


# Delete a category
@app.route('/category/<int:category_id>/delete/', methods=['GET', 'POST'])
def deleteCategoryFunction(category_id):
    category = session.query(Category)
    category2 = session.query(Category).filter_by(id=category_id).first()

    if not hasattr(category2, 'id'):
        return "this category does not exist"
    if 'username' not in login_session:
        # If the user is not logged in, redirect back to log in page
        return redirect('/login')
    if login_session['user_id'] != category2.user_id:
        # If the user who created the category
        # is not the one who is logged in now
        flash("Sorry, you cannot delete this category.")
        # That person is not authorized to delete the category
        return redirect(url_for('catalogFunction'))
    if request.method == 'POST':
        deleteItem = session.query(Item).filter_by(
                                        category_id=category2.id).delete()
        session.delete(category2)
        session.commit()  # Committing to the session to delete the category
        flash('%s is successfully Deleted' % category2.name)
        return redirect(url_for('catalogFunction', m_instruments=category))
        # Redirected to catalog page
    else:
        return render_template('deleteCategory.html', category2=category2)


# Create route to display the items of the category
@app.route('/category/<int:category_id>/items')
def categoryFunction(category_id):
    category = session.query(Category)
    category2 = session.query(Category).filter_by(id=category_id).first()
    # Check if the inserted category id exist in database
    if not hasattr(category2, 'id'):
        return "this category not exist"
    items = session.query(Item).filter_by(category_id=category2.id)

    # If the user is not logged in, show the public page
    if 'username' not in login_session:
        # Checking if there are any items in the category
        if items.count() == 0:
            flash("You have no items yet.")
            return render_template(
                'publicCategory.html',
                m_instruments=category, m_instruments2=category2,
                itemName=items)
        else:
            return render_template(
                'publicCategory.html',
                m_instruments=category, m_instruments2=category2,
                itemName=items)
    # If the user is logged in, show the logged in page
    else:
        # Check if have items in db
        if items.count() == 0:
            flash("You have no items yet.")
            return render_template(
                'category.html',
                m_instruments=category, m_instruments2=category2,
                itemName=items)
        else:
            return render_template(
                'category.html',
                m_instruments=category, m_instruments2=category2,
                itemName=items)

# Create the app.route function to display the item
@app.route('/category/<int:category_id>/items/<int:item_id>')
def itemFunction(category_id, item_id):
    category2 = session.query(Category).filter_by(id=category_id).first()
    # Check if category is there in the database
    if not hasattr(category2, 'id'):
        return "this category not exist"
    items = session.query(Item).filter_by(id=item_id).first()
    # Check if the items exist in the database
    if not hasattr(items, 'id'):
        return "this item not exist"

    if items.category_id != category_id:
        return "This item not exist in this category"
    # If user is not logged in, redirect to the login page
    if 'username' not in login_session:
        return render_template(
            'publicItem.html', itemName=items, category=category2)
    else:
        return render_template('item.html', itemName=items, category=category2)


# Create a new item in the category
@app.route('/category/<int:category_id>/items/new/', methods=['GET', 'POST'])
def newItemFunction(category_id):
    category = session.query(Category)
    category2 = session.query(Category).filter_by(id=category_id).first()
    if not hasattr(category2, 'id'):
        return "this category does not exist"
    if 'username' not in login_session:
        # If the user is not logged in, redirect to login page
        return redirect('/login')

    if request.method == 'POST':
        newItem = Item(
            name=request.form['name'], description=request.form['description'],
            category_id=request.form[
                'category'], user_id=login_session['user_id'])
        # Request form to create a new item
        session.add(newItem)
        session.commit()
        flash('New %s Item is successfully created' % (newItem.name))
        # Flash message that new item is successfully created
        return redirect(url_for(
            'categoryFunction', category_id=newItem.category_id))
    else:
        return render_template(
            'newItem.html', category=category, category2=category2)

# Edit a menu item
@app.route('/category/<int:category_id>/items/<int:item_id>/edit',
           methods=['GET', 'POST'])
# Editing the items in the categories
def editItemFunction(category_id, item_id):

    category = session.query(Category)
    category2 = session.query(Category).filter_by(id=category_id).first()
    if not hasattr(category2, 'id'):
        return "this category not exist"
    editItem = session.query(Item).filter_by(id=item_id).first()
    # Checking if the inserted items are there in the database
    if not hasattr(editItem, 'id'):
        return "this item not exist"

    if editItem.category_id != category_id:
        return "This item not exist in this category"
    # If the user is not logged in, redirect back to the main page
    if 'username' not in login_session:
        return redirect('/login')
    # If the user is not the creator of the item, display an error message
    if login_session['user_id'] != editItem.user_id:
        flash("You not authorized to edit this item.")
        return redirect(url_for('catalogFunction'))

    if request.method == 'POST':  # Request form for making changes
        if request.form['name']:
            editItem.name = request.form['name']
        if request.form['description']:
            editItem.description = request.form['description']
        if request.form['category']:
            editItem.category_id = request.form['category']

        session.add(editItem)
        session.commit()
        flash(' Item Successfully Edited')
        # Flashing message that item was successfully edited
        return redirect(url_for(
            'categoryFunction',
            category_id=editItem.category_id, item_id=item_id))
    else:
        return render_template(
            'editItem.html',
            category=category, category2=category2, editItem=editItem)


# Delete an item in a category
@app.route('/category/<int:category_id>/items/<int:item_id>/delete',
           methods=['GET', 'POST'])
def deleteItemFunction(category_id, item_id):
    category2 = session.query(Category).filter_by(id=category_id).first()

    if not hasattr(category2, 'id'):
        return "this category not exist"
    deleteItem = session.query(Item).filter_by(id=item_id).first()

    if not hasattr(deleteItem, 'id'):
        return "this item not exist"

    if deleteItem.category_id != category_id:
        return "This item not exist in this category"
    # If user is not logged in, redirect to the login page
    if 'username' not in login_session:
        return redirect('/login')
    # If the logged in user is not the creator of the item,
    # show an authorization message
    if login_session['user_id'] != deleteItem.user_id:
        flash("You not authorized to delete this item.")
        return redirect(url_for('catalogFunction'))
    if request.method == 'POST':
        session.delete(deleteItem)
        session.commit()  # Deleting the item
        flash(' Item Successfully Deleted')
        # Flashing a message saying item was deleted
        return redirect(url_for('categoryFunction', category_id=category2.id))
    else:
        return render_template(
            'deleteItem.html', category_id=category_id, item=deleteItem)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True  # To debug the function
    app.run(host='0.0.0.0', port=5000)
    # To open the website on localhost:5000
