from flask import Flask, jsonify, request
from pymongo import MongoClient
import os

import parameters
from validators import hamburger_creator, hamburger_search_by_id, ingredient_creator, ingredient_search_by_id, hamburger_update

app = Flask(__name__)

# Connect to MongoDB
uri = "mongodb+srv://welch_hamburger_api:"+parameters.mongo_password+"@cluster0-cy0hv.mongodb.net/test?retryWrites=true&w=majority"
#uri = os.environ.get('MONGO_URL')
client = MongoClient(uri)
db = client.get_database()

# Obtain Collections
hamburgers = db.hamburgers
ingredients = db.ingredients
hamburgers_ingredients = db.hamburgers_ingredients
counters = db.counters

# Initialize counters
burger_counter = {'burger_counter': 0}
ingredient_counter = {'ingredient_counter': 0}

#burger_counter_init_list = list(counters.find)
burger_init = list(counters.find({"burger_counter": {"$exists": "true", "$ne": "false"}}))
ingredients_init = list(counters.find({"ingredient_counter": {"$exists": "true", "$ne": "false"}}))

print("Burger Init: ", burger_init)
if not burger_init:
    counters.insert_one(burger_counter)
if not ingredients_init:
    counters.insert_one(ingredient_counter)

@app.route("/")
def hello_world():
    return jsonify({"about": "Hello World"})

# Returns all Burgers
@app.route("/hamburguesa", methods=["GET"])
def hamburguesa_get():

    response_list = list()
    all_hamburgers = list(hamburgers.find({}, {"_id": 0}))

    for burger in all_hamburgers:
        burger_ingredients_paths = list()
        burger_ingredients_list = list(hamburgers_ingredients.find({"hamburguesa_id": burger["id"]}, {"_id": 0}))

        for ingredient in burger_ingredients_list:
            print(ingredient)
            p = {"path": "https://link.com/ingrediente/"+str(ingredient["ingrediente_id"])}
            burger_ingredients_paths.append(p)
        burger["ingredientes"] = burger_ingredients_paths
        response_list.append(burger)
    return jsonify(response_list), 200

# Creates new burger
@app.route("/hamburguesa", methods=["POST"])
def hamburguesa_post():

    data = request.get_json()
    valid = hamburger_creator(data)

    if valid['status'] == 'valid input':
        #new_id = list(counters.find({"burger_counter"}, {"_id": 0}))
        #print("New ID: ", new_id)
        ids_list = list(counters.find({}, {"_id": 0}))
        ids = dict()
        for counter in ids_list:
            ids.update(counter)
        data["id"] = ids["burger_counter"]
        new_id = {"$set": {"burger_counter": data["id"] + 1}}
        counters.update_one({"burger_counter": data["id"]}, new_id)
        inserted_burger = hamburgers.insert_one(data)
        hamburgers_list = list(hamburgers.find({"id": data['id']}, {"_id": 0}))
        response = hamburgers_list[0]
        burger_ingredients = list(hamburgers_ingredients.find({"hamburguesa_id": data['id']}))
        ingredient_list = list()
        for ingredient in burger_ingredients:
            print("Ingredient: ", ingredient, "\n")
            p = {"path": "https://link.com/ingredientes/" +
                    str(ingredient['ingrediente_id'])}
            ingredient_list.append(p)
        response['ingredientes'] = ingredient_list
        return jsonify(response), 201
    
    else:
        #response = {'status': 'input invalido'}
        return jsonify(), 400

# Searches burger with id: id
@app.route("/hamburguesa/<string:id>")
def hamburguesa_get_by_id(id):

    ids_list = list(counters.find({}, {"_id": 0}))
    ids = dict()
    for counter in ids_list:
        ids.update(counter) 
    
    valid = hamburger_search_by_id(id)
    if valid['status'] == 'invalid id':
        #response = {'status': 'id invalido'}
        return jsonify(), 400
    else:
        hamburgers_list = list(hamburgers.find({"id": int(id)}, {"_id": 0}))
        if len(hamburgers_list) == 0:
            #response = {'status': 'hamburguesa inexistente'}
            return jsonify(), 404
        else:
            response = hamburgers_list[0]
            burger_ingredients = list(hamburgers_ingredients.find({"hamburguesa_id": int(id)}))
            ingredient_list = list()
            for ingredient in burger_ingredients:
                print("Ingredient: ", ingredient, "\n")
                p = {"path": "https://link.com/ingredientes/"+str(ingredient['ingrediente_id'])}
                ingredient_list.append(p)
            response['ingredientes'] = ingredient_list
            return jsonify(response), 200

# Deletes burger with id: id
@app.route("/hamburguesa/<string:id>", methods=["DELETE"])
def hamburguesa_delete(id):

    valid = hamburger_search_by_id(id)

    if valid['status'] == 'valid id':
        hamburgers_list = list(hamburgers.find({"id": int(id)}))
        if len(hamburgers_list) == 0:
            #response = {'status': 'hamburguesa inexistente'}
            return jsonify(), 404
        else:
            hamburgers_ingredients.delete_many({"hamburguesa_id": int(id)})
            hamburgers.delete_many({"id": int(id)})
            #response = {'status': 'hamburguesa eliminada'}
            return jsonify(), 200
    else:
        #response = {'status': 'input invalido'}
        return jsonify(), 400

# Updates burger information
@app.route("/hamburguesa/<string:id>", methods=["PATCH"])
def hamburguesa_patch(id):

    data = request.get_json()
    valid_id = hamburger_search_by_id(id)

    if valid_id['status'] == 'valid id':
        current_burger = list(hamburgers.find({"id": int(id)}, {"_id": 0}))
        if len(current_burger) == 0:
            #response = {'status': 'hamburguesa inexistente'}
            return jsonify(), 404
        else:
            valid_update = hamburger_update(current_burger, data)
            if valid_update['status'] == 'valid update':
                new_values = {"$set": data}
                print("MADE IT HERE/n")
                hamburgers.update_one(current_burger[0], new_values)
                #response = {'status': 'operacion exitosa'}
                #response = hamburguesa_get_by_id(id)
                hamburgers_list = list(
                    hamburgers.find({"id": int(id)}, {"_id": 0}))
                response = hamburgers_list[0]
                burger_ingredients = list(
                    hamburgers_ingredients.find({"hamburguesa_id": int(id)}))
                ingredient_list = list()
                for ingredient in burger_ingredients:
                    print("Ingredient: ", ingredient, "\n")
                    p = {"path": "https://link.com/ingredientes/" +
                        str(ingredient['ingrediente_id'])}
                    ingredient_list.append(p)
                response['ingredientes'] = ingredient_list
                return jsonify(response), 200
            else:
                #response = {'status': 'parametros invalidos'}
                return jsonify(), 400
    else:
        #response = {'status': 'parametros invalidos'}
        return jsonify(), 400

# Removes ingredient from burger
@app.route("/hamburguesa/<string:burger_id>/ingrediente/<string:ingredient_id>", methods=["DELETE"])
def remove_ingrediente_hamburguesa(burger_id, ingredient_id):
    
    valid_burger_id = hamburger_search_by_id(burger_id)
    valid_ingredient_id = ingredient_search_by_id(ingredient_id)

    if valid_burger_id['status'] == 'invalid id':
        #response = {'status': 'id de hamburguesa invalido'}
        return jsonify(), 400
    else:
        if valid_ingredient_id['status'] == 'invalid id':
            #response = {'status': 'id de ingrediente invalido'}
            return jsonify(), 400
        else:
            hamburgers_list = list(hamburgers.find({"id": int(burger_id)}, {"_id": 0}))
            if len(hamburgers_list) == 0:
                #response = {'status': 'hamburguesa inexistente'}
                return jsonify(), 404
            else:
                hamburgers_ingredients_list = list(hamburgers_ingredients.find({"hamburguesa_id": int(burger_id), "ingrediente_id": int(ingredient_id)}, {"_id": 0}))
                if len(hamburgers_ingredients_list) == 0:
                    #response = {'status': 'ingrediente inexistente en la hamburguesa'}
                    return jsonify(), 404
                else:
                    hamburgers_ingredients.delete_many({"hamburguesa_id": int(burger_id), "ingrediente_id": int(ingredient_id)})
                    #response = {'status': 'ingrediente retirado'}
                    return jsonify(), 200

# Adds ingredient on burger
@app.route("/hamburguesa/<string:burger_id>/ingrediente/<string:ingredient_id>", methods=["PUT"])
def hamburguesa_put_ingrediente(burger_id, ingredient_id):
    
    valid_burger_id = hamburger_search_by_id(burger_id)
    valid_ingredient_id = ingredient_search_by_id(ingredient_id)

    if valid_burger_id['status'] == 'invalid id':
        #response = {'status': 'id de hamburguesa invalido'}
        return jsonify(), 400
    else:
        if valid_ingredient_id['status'] == 'invalid id':
            #response = {'status': 'id de ingrediente invalido'}
            return jsonify(), 400
        else:
            hamburgers_list = list(
                hamburgers.find({"id": int(burger_id)}, {"_id": 0}))
            if len(hamburgers_list) == 0:
                #response = {'status': 'hamburguesa inexistente'}
                return jsonify(), 404
            else:
                ingredients_list = list(ingredients.find({"id": int(ingredient_id)}, {"_id": 0}))
                if len(ingredients_list) == 0:
                    #response = {'status': 'ingrediente inexistente'}
                    return jsonify(), 404
                else:
                    data = {"hamburguesa_id": hamburgers_list[0]["id"], "ingrediente_id": ingredients_list[0]["id"]}
                    
                    hamburgers_ingredients_list = list(hamburgers_ingredients.find(
                        {"hamburguesa_id": hamburgers_list[0]["id"], "ingrediente_id": ingredients_list[0]["id"]}))
                    if len(hamburgers_ingredients_list) == 0:
                        hamburgers_ingredients.insert_one(data)
                    #response = {'status': 'ingrediente agregado'}
                    return jsonify(), 201

@app.route("/ingrediente", methods=["GET"])
def ingredient_get():
    all_ingredients = list(ingredients.find({}, {"_id": 0}))
    return jsonify(all_ingredients), 200

@app.route("/ingrediente/<string:id>", methods=["GET"])
def ingrediente_get_by_id(id):

    valid = ingredient_search_by_id(id)
    if valid['status'] == 'invalid id':
        #response = {'status': 'id invalido'}
        return jsonify(), 400
    else:
        ingredients_list = list(ingredients.find({"id": int(id)}, {"_id": 0}))
        if len(ingredients_list) == 0:
            #response = {'status': 'ingrediente inexistente'}
            return jsonify(), 404
        else:
            response = ingredients_list[0]
            return jsonify(response), 200

# Creates new ingredient
@app.route("/ingrediente", methods=["POST"])
def ingredient_post():

    data = request.get_json()
    valid = ingredient_creator(data)

    if valid['status'] == 'valid input':
        ids_list = list(counters.find({}, {"_id": 0}))
        ids = dict()
        for counter in ids_list:
            ids.update(counter)
        data["id"] = ids["ingredient_counter"]
        new_id = {"$set": {"ingredient_counter": data["id"] + 1}}
        counters.update_one({"ingredient_counter": data["id"]}, new_id)

        #data["id"] = parameters.current_ingredient_id
        #parameters.current_ingredient_id += 1
        inserted_ingredient = ingredients.insert_one(data)
        print("Inserted Ingredient: ", inserted_ingredient)
        #response = {"status": "ingrediente creado"}
        #response = ingrediente_get_by_id(str(data["id"]))
        ingredients_list = list(ingredients.find({"id": data["id"]}, {"_id": 0}))
        response = ingredients_list[0]
        return jsonify(response), 201
    else:
        #response = {"status": "Input invalido"}
        return jsonify(), 400

@app.route("/ingrediente/<string:id>", methods=["DELETE"])
def ingredient_delete(id):
    
    valid = ingredient_search_by_id(id)

    if valid['status'] == 'valid id':
        ingredient_list = list(ingredients.find({"id": int(id)}))
        if len(ingredient_list) == 0:
            #response = {'status': 'ingrediente inexistente'}
            return jsonify(), 404
        else:
            # Check if ingredient is currently being used
            hamburgers_ingredients_list = list(hamburgers_ingredients.find({"ingrediente_id": int(id)}))
            if len(hamburgers_ingredients_list) == 0:
                ingredients.delete_many({"id": int(id)})
                #response = {'status': 'ingrediente eliminado'}
                return jsonify(), 200
            else:
                #response = {'status': 'ingrediente no se puede borrar, se encuentra presente en una hamburguesa'}
                return jsonify(), 409
    else:
        #response = {'status': 'input invalido'}
        return jsonify(), 400

if __name__ == "__main__":
    app.run(debug=True)
