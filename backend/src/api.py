import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app, resources={r'/*': {'origins': '*'}})

# set up cors headers
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
    response.headers.add('Access-Control-Allow-Methods', 'GET, PUT, POST, DELETE, OPTIONS')
    return response

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES

#  get drinks with some drinks' details
@app.route('/drinks')
def get_drinks():
    try:
        drinks = Drink.query.all()
        formatted_drinks = [drink.short() for drink in drinks]
        print(formatted_drinks)
        return jsonify({
            'success': True,
            'drinks': formatted_drinks
        }), 200
    except:
        abort(422)
   





#get drinks with all drinks' details
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_details():
    try:
        drinks = Drink.query.all()
        formatted_drinks = [drink.long() for drink in drinks]
        return jsonify({
            'success': True,
            'drinks': formatted_drinks
        }), 200
    except:
        abort(422)

# create a drink
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink():
    try:
        body = request.get_json()
        title = body.get('title')
        recipe = body.get('recipe')
        drink = Drink(title=title, recipe=json.dumps(recipe))
        drink.insert()
        return jsonify({
            "success": True,
            "drinks": drink.long()
        }), 200
        
    except:
        abort(422)

# update a drink
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(drink_id):
    try:
        body = request.get_json()
        drink = Drink.query.get(drink_id)
        if drink is None:
            abort(404)

        title = body.get('title')
        recipe = body.get('recipe')
        if recipe:
            drink.recipe = json.dumps(recipe)
       
        drink.title = title
        drink.update()
        return jsonify({
            "success": True,
            "drinks": drink.long()
        })
    except:
        abort(422)

# delete a drink
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(drink_id):
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        drink.delete()
        return jsonify({
            'success': True,
            'delete': drink_id
        }), 200
    except:
        abort(404)


# Error Handling
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False, 
        "error": 422,
        "message": "unprocessable"
    }), 422

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(401)
def not_found(error):
    return jsonify({
        "success": False, 
        "error": 401,
        "message": "Unauthorized"
    }), 401

@app.errorhandler(403)
def not_found(error):
    return jsonify({
        "success": False, 
        "error": 403,
        "message": "Forbidden"
    }), 403

@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        'error': 500,
        'message': "Internal Server Error"
    }), 500


@app.errorhandler(AuthError)
def auth_error(error):
    error_msg = error.args
    message = error_msg[0]
    status_code = error_msg[1]
    return jsonify({
        "success": False,
        "error": status_code,
        "message": message.get('description')
    }), status_code

if __name__ == '__main__':
    app.run()
