from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from utils import Generate_token

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/foodly"
mongo = PyMongo(app)

@app.route("/register", methods=['POST'])
def register():
    username = request.args["username"]
    password = request.args["password"]
    phone = request.args["phone"]
    role = request.args["role"]
    if not role in ["customer", "restaurent"]:
        return jsonify({"error":"bad role"}), 403
    try:
        mongo.db.users.insert_one({
            "username": username,
            "password": password, #TODO:hash password for security stuff
            "phone": phone,
            "role": role
        })
    except Exception as e:
        print(e)
        return jsonify({"error":"unkown error occured"}), 500 #TODO:more error handeling
    token = Generate_token(mongo)
    mongo.db.tokens.insert_one({"token": token, "username": username})
    return jsonify({"token":token})

@app.route('/login', methods=['POST'])
def login():
    username = str(request.args["username"])
    password = str(request.args["password"])
    tokens = list(mongo.db.tokens.find({"username": username}))
    if len(tokens) == 1 and list(mongo.db.users.find({"username": username}))[0]["password"] == password:
        return jsonify({"token":tokens[0]["token"]}), 200
    else:
        return jsonify({"error":"something went wrong"}), 403

@app.route("/submit/food", methods=["POST"])
def SubmitFood():
    token = request.args["token"]
    username = request.args["username"]
    print(f"{token} {username}")
    QueryToken = list(mongo.db.tokens.find({}))
    print(QueryToken)
    if QueryToken[0]["username"] == username:
        QueryFood = mongo.db.foods.insert_one({
            "restaurent": str(username),
            "name": str(request.args["name"]),
            "description": str(request.args["desc"]),
            "price": str(request.args["price"]) #TODO:add image
        })
        print(QueryFood)

        return jsonify({"status":"done"})

if __name__ == "__main__":
    app.run("0.0.0.0", 5000, debug=True)
