from flask import Flask, jsonify, request
from pymongo import MongoClient

import parameters
from validators import hamburger_creator, hamburger_search_by_id, ingredient_creator

app = Flask(__name__)

# Connect to MongoDB
uri = "mongodb+srv://welch_hamburger_api:"+parameters.mongo_password+"@cluster0-cy0hv.mongodb.net/test?retryWrites=true&w=majority"
client = MongoClient(uri)
db = client.get_database()

# Obtain Collections
hamburgers = db.hamburgers
ingredients = db.ingredients
hamburgers_ingredients = db.hamburgers_ingredients

@app.route("/")
def hello_world():
    return jsonify({"about": "Hello World"})

# Returns all Burgers
@app.route("/hamburguesa", methods=["GET"])
def hamburguesa_get():
    all_hamburgers = list(hamburgers.find({}, {"_id": 0}))
    print(f"Burgers: {all_hamburgers}")
    return jsonify(all_hamburgers), 200

# Creates new burger
@app.route("/hamburguesa", methods=["POST"])
def hamburguesa_post():

    data = request.get_json()
    valid = hamburger_creator(data)

    if valid['status'] == 'valid input':
        data['id'] = parameters.current_burger_id
        parameters.current_burger_id += 1
        inserted_burger = hamburgers.insert_one(data)
        response = {'status': 'hamburguesa creada'}
        return jsonify(response), 201
    
    else:
        response = {'status': 'input invalido'}
        return jsonify(response), 400

# Searches burger with id: id
@app.route("/hamburguesa/<string:id>")
def hamburguesa_get_by_id(id):

    valid = hamburger_search_by_id(id)
    if valid['status'] == 'invalid id':
        response = {'status': 'id invalido'}
        return jsonify(response), 400
    else:
        hamburgers_list = list(hamburgers.find({"id": int(id)}, {"_id": 0}))
        if len(hamburgers_list) == 0:
            response = {'status': 'hamburguesa inexistente'}
            return jsonify(response), 404
        else:
            response = hamburgers_list[0]
            return jsonify(response), 200


@app.route("/ingrediente", methods=["GET"])
def ingredient_get():
    all_ingredients = list(ingredients.find({}, {"_id": 0}))
    return jsonify(all_ingredients), 200


# Creates new ingredient
@app.route("/ingrediente", methods=["POST"])
def ingredient_post():

    data = request.get_json()
    valid = ingredient_creator(data)

    if valid['status'] == 'valid input':
        inserted_ingredient = ingredients.insert_one(data)
        print("Inserted Ingredient: ", inserted_ingredient)
        response = {"status": "ingrediente creado"}
        return jsonify(response), 201
    else:
        response = {"status": "Input invalido"}
        return jsonify(response), 400

if __name__ == "__main__":
    app.run(debug=True)
