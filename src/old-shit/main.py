#************************************************************************************
#
#                                   API URL Routing Page
#
#************************************************************************************
import flask
from flask import Flask, jsonify, request, current_app
from flask_cors import CORS
from functools import wraps, update_wrapper
from markupsafe import escape
from User import User
from Login import Login
from DB import DB
from Product_Categories import ProductCategories
from Product import Product
from Utilities import Utilities
from Product_Availability import ProductAvailability
import os
from Globals import Globals
from CustomJSONEncoder import CustomJSONEncoder

# setup the flask application
app = Flask(__name__)

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.json_encoder = CustomJSONEncoder

CORS(app)

# setup the global variables container
requestGlobals = Globals(client_id=None)

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        # if user is not logged in, redirect to login page
        if not request.authorization:
            flask.abort(401)
        
        # make sure the user is authorized
        clientID = Login.getUserID(request.authorization.username, request.authorization.password)
        if clientID == None:
            flask.abort(401)
        
        global requestGlobals
        requestGlobals.client_id = clientID

        # finally call f. f() now haves access to g.user
        return f(*args, **kwargs)

    return wrap

#************************************************************************************
#
#                                   Index
#
#************************************************************************************
@app.route('/')
def home():   
    return 'Welcome to the WMIYS api!'

#************************************************************************************
#
#                                   Users
#
#************************************************************************************

#------------------------------------------------------
# Create new user
#------------------------------------------------------
@app.route('/users', methods=['POST'])
def users():
    new_user = User()

    # set the user properties
    new_user.email      = request.form.get('email') or None
    new_user.password   = request.form.get('password') or None
    new_user.name_first = request.form.get('name_first') or None
    new_user.name_last  = request.form.get('name_last') or None
    new_user.birth_date = request.form.get('birth_date') or None
    
    new_user.insert()
    new_user.fetch()

    return jsonify(new_user.__dict__)


#------------------------------------------------------
# Get a single user
#------------------------------------------------------
@app.route('/users/<int:user_id>', methods=['GET'])
@login_required
def user(user_id):
    # make sure the user is authorized
    if requestGlobals.client_id != user_id:
        flask.abort(403)

    user = User(id=user_id)
    user.fetch()

    return jsonify(user.as_dict(return_password=False))


#************************************************************************************
#
#                                   Login
#
#************************************************************************************
@app.route('/login', methods=['GET'])
def login():
    userID = Login.getUserID(request.args['email'], request.args['password'])

    # make sure the user is authorized
    if userID == None:
        flask.abort(404)

    user = User(id=userID)
    user.fetch()
    return jsonify(user.as_dict(False))


#************************************************************************************
#
#                               Search
#
#************************************************************************************
#------------------------------------------------------
# Locations
#------------------------------------------------------
@app.route('/search/locations', methods=['GET'])
def searchLocations():
    query = request.args.get('q')

    # make sure the q argumrnt is set by the client
    if query == None:
        flask.abort(400)

    # if no per_page argument was given or it's gt 100, set it to the default (20)
    per_page = request.args.get('per_page')
    if per_page == None or int(per_page) > 100:
        per_page = 20
    
    search_results = DB.searchLocations(query=query, num_results=per_page)

    return jsonify(search_results)


#************************************************************************************
#
#                           Product Categories
#
#************************************************************************************
#------------------------------------------------------
# All categories
#------------------------------------------------------
@app.route('/product-categories', methods=['GET'])
def productCatgories():
    return jsonify(ProductCategories.getAll())

#------------------------------------------------------
# all major categories
#------------------------------------------------------
@app.route('/product-categories/major', methods=['GET'])
def productCategoriesMajors():
    return jsonify(ProductCategories.getMajors())

#------------------------------------------------------
# single major category
#------------------------------------------------------
@app.route('/product-categories/major/<int:major_id>', methods=['GET'])
def productCategoriesMajor(major_id):
    return jsonify(ProductCategories.getMajor(major_id))

#------------------------------------------------------
# all minor categories of a major
#------------------------------------------------------
@app.route('/product-categories/major/<int:major_id>/minor', methods=['GET'])
def productCategoriesMinors(major_id):
    return jsonify(ProductCategories.getMinors(major_id))

#------------------------------------------------------
# single minor category
#------------------------------------------------------
@app.route('/product-categories/major/<int:major_id>/minor/<int:minor_id>', methods=['GET'])
def productCategoriesMinor(major_id, minor_id):
    return jsonify(ProductCategories.getMinor(minor_id))

#------------------------------------------------------
# all sub categories of a minor
#------------------------------------------------------
@app.route('/product-categories/major/<int:major_id>/minor/<int:minor_id>/sub', methods=['GET'])
def productCategoriesSubs(major_id, minor_id):
    return jsonify(ProductCategories.getSubs(minor_id))

#------------------------------------------------------
# single sub category
#------------------------------------------------------
@app.route('/product-categories/major/<int:major_id>/minor/<int:minor_id>/sub/<int:sub_id>', methods=['GET'])
def productCategoriesSub(major_id, minor_id, sub_id):
    return jsonify(ProductCategories.getSub(sub_id))


#************************************************************************************
#
#                           Products
#
#************************************************************************************

#------------------------------------------------------
# Fetch all of a user's products
#------------------------------------------------------
@app.route('/users/<int:user_id>/products', methods=['GET'])
@login_required
def userProductsGet(user_id):
    # make sure the user is authorized
    if requestGlobals.client_id != user_id:
        flask.abort(403)

    userProducts = DB.getUserProducts(user_id)

    return jsonify(userProducts)

#------------------------------------------------------
# Create a new product
#------------------------------------------------------
@app.route('/users/<int:user_id>/products', methods=['POST'])
@login_required
def userProductsPost(user_id):    
    # make sure the user is authorized
    if requestGlobals.client_id != user_id:
        flask.abort(403)

    newProduct = Product()

    # set the object properties from the fields in the request body
    # if the request body contains an invalid field, abort
    if not newProduct.setPropertyValuesFromDict(request.form.to_dict()):
        flask.abort(400)

    newProduct.user_id = user_id    # user_id is in the URI

    # set the image if one was uploaded
    if request.files.get('image'):
        newProduct.setImagePropertyFromImageFile(request.files.get('image'), Product.LOCAL_SERVER_COVER_PHOTO_DIRECTORY)
    
    newProduct.insert()

    return jsonify(newProduct.get())


#------------------------------------------------------
# Retrieve/update a single user product
#------------------------------------------------------
@app.route('/users/<int:user_id>/products/<int:product_id>', methods=['GET', 'PUT'])
@login_required
def productRequest(user_id, product_id):
    # load the product data
    product = Product(id=product_id)
    product.loadData()  # load the product data from the database

    if request.method == 'PUT':
        # the request body contained a field that does not belong in the product class
        if not product.setPropertyValuesFromDict(request.form.to_dict()):
            flask.abort(400)

        # set the image if one was uploaded
        if request.files.get('image'):
            product.setImagePropertyFromImageFile(request.files.get('image'), Product.LOCAL_SERVER_COVER_PHOTO_DIRECTORY)

        updateResult = product.update()

        return ('', 200)
    else:
        return jsonify(product.get())



#************************************************************************************
#
#                           Product Availability
#
#************************************************************************************

#------------------------------------------------------
# Retrieve all the product availabilities of a single product
#------------------------------------------------------
@app.route('/users/<int:user_id>/products/<int:product_id>/availability', methods=['GET'])
@login_required
def productAvailabilities(user_id: int, product_id: int):
    # make sure the user is authorized
    if requestGlobals.client_id != user_id:
        flask.abort(403)

    # get the availabilities
    availabilities = ProductAvailability.getProductAvailabilities(product_id)
    return jsonify(availabilities)


#------------------------------------------------------
# Create a new product availability
#------------------------------------------------------
@app.route('/users/<int:user_id>/products/<int:product_id>/availability', methods=['POST'])
@login_required
def productAvailabilityPost(user_id: int, product_id: int):
    # make sure the user is authorized
    if requestGlobals.client_id != user_id:
        flask.abort(403)

    # get the availabilities
    availability = ProductAvailability(product_id=product_id)
    
    # set the objects properties to the fields in the request body
    if not availability.setPropertyValuesFromDict(request.form.to_dict()):
        flask.abort(400)    # the request body contained a field that does not belong in the product class
    
    availability.insert()

    return jsonify(availability.get())


#------------------------------------------------------
# Retrieve all the product availabilities of a single product
#------------------------------------------------------
@app.route('/users/<int:user_id>/products/<int:product_id>/availability/<int:product_availability_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def productAvailability(user_id: int, product_id: int, product_availability_id: int):
    # make sure the user is authorized
    if requestGlobals.client_id != user_id:
        flask.abort(403)

    availability = ProductAvailability(id=product_availability_id)
    
    if request.method == 'GET':
        return jsonify(availability.get())
    
    elif request.method == 'PUT':
        availability.loadData() # load the current values into the object properties

        # set the objects properties to the fields in the request body
        if not availability.setPropertyValuesFromDict(request.form.to_dict()):
            flask.abort(400)    # the request body contained a field that does not belong in the product class
    
        dbResult = availability.update()    # update the database

        return jsonify(availability.get())
        
    elif request.method == 'DELETE':
        result = availability.delete()

        if result.rowcount != 1:
            pass    # error something went wrong
        
        return ('', 204)



#************************************************************************************
#
#                           Main loop
#
#************************************************************************************
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
