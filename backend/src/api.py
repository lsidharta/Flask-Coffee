import os
from flask import Flask, request, jsonify, abort, Response
from http import HTTPStatus
from functools import wraps
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
#with app.app_context():
#    db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
@requires_auth('get:drinks')
def get_drinks(jwt):
    query = Drink.query.all()
    '''
    Reference: https://knowledge.udacity.com/questions/327463
    '''
    drinks = list(map(Drink.short, Drink.query.all()))
    result = {
        "success": True,
        "drinks": drinks
    }
    return jsonify(result, 200)

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    try:
        query = Drink.query.all()
        '''
        Reference: https://knowledge.udacity.com/questions/327463
        '''
        drinks = list(map(Drink.long, Drink.query.all()))
        if not drinks:
            print("There is no drink in database.")
            abort(404)

        result = {
            "success": True,
            "drinks": drinks
        }
        return jsonify(result, 200)
    except Exception as e:
        print(e)
        abort(422)

    '''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drinks(jwt):
    try:
        body = request.get_json()
        #body = request.data
        if body:
            new_data = json.loads(body.decode('utf-8'))
            old_drinks = Drink.query.count()
            #print(new_data)
            drink_obj = Drink(
                            id=old_drinks+1,
                            title=new_data['title'],
                            recipe=json.dumps(new_data['recipe'])
                        )
            Drink.insert(drink_obj)
            drinks = Drink.query.all()#list(map(Drink.long, Drink.query.all()))
            print(len(drinks))
            drinks_array = list(map(Drink.long, drinks))
            print(drinks_array)
            if not drinks:
                print("There is no drink in database.")
                abort(404)

            result = {
                "success": True,
                "drinks": drinks_array
            }
            return jsonify(result, 200)
    except Exception as e:
        print(e)
        abort(422)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(jwt, drink_id):
    try:
        # Get the info from frontend
        body = request.get_json()
        new_title = body.get('title', None)
        new_recipe = body.get('recipe', None)
        
        # Get the record from database
        drink_obj = Drink.query.filter(Drink.id == int(drink_id)).one_or_none()
        
        if drink_obj is None:
            abort(404)
        
        drink_obj.title = new_title
        drink_obj.recipe = json.dumps(new_recipe)
        drink_obj.update()

        result = {
            'success': True,
            'drinks': json.dumps(drink_obj.long())
            }
        return jsonify(result, 200)

    except Exception as e:
        print(e)
        abort(422)

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(jwt, drink_id):
    try:
        drink_obj = Drink.query.filter(Drink.id == int(drink_id)).one_or_none()
        print(drink_id)
        # Throw error 404 if drink_obj is not found
        if drink_obj is None:
            abort(404)

        drink_obj.delete()

        return jsonify({
            'success': True,
            'delete': drink_id
        }, 200)
    except Exception as e:
        print(e)
        abort(422)

# Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
'''
Reference: https://knowledge.udacity.com/questions/936217
'''
@app.errorhandler(AuthError)
def handle_auth_error(ex):
    '''
    Receive the raised authorization error and propagates it as response
    '''
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return(response)

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
'''
Reference: https://knowledge.udacity.com/questions/538174
'''
@app.route('/drinks/<int:drink_id>')
@requires_auth('get:drinks')
@app.errorhandler(AuthError)
def get_specific_drink_test_1(jwt, drink_id):
    '''
    Function to test the implementation of error handler 404
    '''
    print(drink_id)
    try:
        drink_obj = Drink.query.filter(Drink.id == int(drink_id)).one_or_none()
        print(drink_obj)
        if drink_obj is None:
            raise AuthError(
                {
                    'success': False,
                    'error': 404,
                    'message': 'resource not found'
                }, 404
            )
        result = {
            "success": True,
            "drinks": drink_obj.long()
        }
        return jsonify(result, 200)

    except Exception as e:
        print(e)
        raise AuthError(
            {
                'success': False,
                'error': 422,
                'message': 'unprocessable'
            }, 422
        )

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
'''
Reference: https://knowledge.udacity.com/questions/538174
'''