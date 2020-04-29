from flask import Flask, jsonify, request
from pymongo import MongoClient, srv

import parameters
from validators import hamburger_creator, hamburger_search_by_id, ingredient_creator, ingredient_search_by_id, hamburger_update

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
@app.route("/hamburguesa", methods=["POST"]) # Missing case where fields are empty 
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

# Deletes burger with id: id
@app.route("/hamburguesa/<string:id>", methods=["DELETE"])
def hamburguesa_delete(id):

    valid = hamburger_search_by_id(id)

    if valid['status'] == 'valid id':
        hamburgers_list = list(hamburgers.find({"id": int(id)}))
        if len(hamburgers_list) == 0:
            response = {'status': 'hamburguesa inexistente'}
            return jsonify(response), 404
        else:
            hamburgers.delete_many({"id": int(id)})
            response = {'status': 'hamburguesa eliminada'}
            return jsonify(response), 200
    else:
        response = {'status': 'hamburguesa inexistente'}
        return jsonify(response), 404

# Updates burger information
@app.route("/hamburguesa/<string:id>", methods=["PATCH"])
def hamburguesa_patch(id):

    data = request.get_json()
    valid_id = hamburger_search_by_id(id)

    if valid_id['status'] == 'valid id':
        current_burger = list(hamburgers.find({"id": int(id)}, {"_id": 0}))
        if len(current_burger) == 0: # Check if it should be 404 or 400
            response = {'status': 'hamburguesa inexistente'}
            return jsonify(response), 404
        else:
            valid_update = hamburger_update(current_burger, data)
            if valid_update['status'] == 'valid update':
                new_values = {"$set": data}
                print("MADE IT HERE/n")
                hamburgers.update_one(current_burger[0], new_values)
                response = {'status': 'operacion exitosa'}
                return jsonify(response), 200
            else:
                response = {'status': 'parametros invalidos'}
                return jsonify(response), 400
            pass
    else:
        response = {'status': 'hamburguesa inexistente'} # Check if it should be 404 or 400
        return jsonify(response), 404

@app.route("/ingrediente", methods=["GET"])
def ingredient_get():
    all_ingredients = list(ingredients.find({}, {"_id": 0}))
    return jsonify(all_ingredients), 200

@app.route("/ingrediente/<string:id>", methods=["GET"])
def ingrediente_get_by_id(id):

    valid = ingredient_search_by_id(id)
    if valid['status'] == 'invalid id':
        response = {'status': 'id invalido'}
        return jsonify(response), 400
    else:
        ingredients_list = list(ingredients.find({"id": int(id)}, {"_id": 0}))
        if len(ingredients_list) == 0:
            response = {'status': 'ingrediente inexistente'}
            return jsonify(response), 404
        else:
            response = ingredients_list[0]
            return jsonify(response), 200

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

@app.route("/ingrediente/<string:id>", methods=["DELETE"])
def ingredient_delete(id): # Missing condition if being used in some burger
    
    valid = ingredient_search_by_id(id)

    if valid['status'] == 'valid id':
        ingredient_list = list(ingredients.find({"id": int(id)}))
        if len(ingredient_list) == 0:
            response = {'status': 'ingrediente inexistente'}
            return jsonify(response), 404
        else:
            # Check if ingredient is currently being used
            # if blah blah
            ingredients.delete_many({"id": int(id)})
            response = {'status': 'ingrediente eliminado'}
            return jsonify(response), 200
    else:
        response = {'status': 'ingrediente inexistente'}
        return jsonify(response), 404

if __name__ == "__main__":
    app.run(debug=True)
