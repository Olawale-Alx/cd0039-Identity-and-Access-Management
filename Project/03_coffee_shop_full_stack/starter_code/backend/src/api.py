import os
from flask import Flask, request, jsonify, abort
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
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    try:
        drinks = [drink.short() for drink in Drink.query.all()]
        return jsonify({
            'success': 'True',
            'drinks': drinks
        }, 200)

    except:
        raise AuthError({
            'code': 'resource not found',
            'description': 'Requested resource cannot be found'
        }, 404)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    try:
        drinks_long = [drink.long() for drink in Drink.query.all()]
        return jsonify({
            'success': 'True',
            'drinks': drinks_long
        }, 200)

    except:
        raise AuthError({
            'code': 'resource not found',
            'description': 'Requested resource cannot be found'
        }, 404)


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
def post_drink(payload):
    new_drink_details = request.get_json()
    try:
        if 'title' and 'recipe' not in new_drink_details:
            raise AuthError({
            'code': 'unprocessable entity',
            'description': 'request could not be processed'
        }, 422)

        title = new_drink_details['title']
        recipe = json.dumps(new_drink_details['recipe'])

        drink = Drink(title=title, recipe=recipe)
        drink.insert()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        }, 200)

    except:
        raise AuthError({
            'code': 'resource not found',
            'description': 'Requested resource cannot be found'
        }, 404)


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
@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink_by_id(payload, id):
    try:
        request_body = request.get_json()
        drink = Drink.query.get(id)
        title = request_body['title']

        if 'recipe' in request_body.keys():
            recipe = json.dumps(request_body['recipe'])

        else:
            recipe = drink.recipe

        drink.title = title
        drink.recipe = recipe
        drink.update()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        }, 200)

    except:
        raise AuthError({
            'code': 'resource not found',
            'description': 'Requested resource cannot be found'
        }, 404)


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
@app.route('/drinks/<id>', metods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink_by_id(payload, id):
    try:
        drink = Drink.query.get(id)
        drink.delete()

        return jsonify({
            'success': True,
            'deleted drink': id
        }, 200)

    except:
        raise AuthError({
            'code': 'resource not found',
            'description': 'Requested resource cannot be found'
        }, 404)


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
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        'success': 'False',
        'error': 404,
        'message': 'Resources not found'
    }, 404)


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code
