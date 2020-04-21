from flask import Flask, jsonify, request
from pymongo import MongoClient

import parameters
from validators import hamburger_creator

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

@app.route("/hamburguesa", methods=["POST"])
def hamburguesa_post():

    data = request.get_json()
    print(data)
    valid = hamburger_creator(data)

    if valid['status'] == 'valid input':
        data['id'] = parameters.current_burger_id
        parameters.current_burger_id += 1
        inserted_burger = hamburgers.insert_one(data)
        print("Inserted Burger: ", inserted_burger)
        response = {'status': 'hamburguesa creada'}
        return jsonify(response), 201
    
    else:
        response = {'status': 'input invalido'}
        return jsonify(response), 400


if __name__ == "__main__":
    app.run(debug=True)
