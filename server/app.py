from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from werkzeug.utils import secure_filename
from flask_cors import CORS
from utils import Generate_token, JSONEncoder, Hash, EmailValidation, usernameNotRepetitious
from datetime import datetime


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/foodly"
app.json_encoder = JSONEncoder
mongo = PyMongo(app)
CORS(app)

@app.route("/ok", methods=['GET'])
def test():
    return jsonify({"status":"OK"})

@app.route("/register", methods=['POST'])
def register():
    username = request.form["username"]
    password = request.form["password"]
    email = request.form["email"]
    role = request.form["role"]
    city = request.form["city"]
    if not role in ["customer", "restaurant"]:
        return jsonify({"error":"bad role"}), 400
    if not EmailValidation(email):
        return jsonify({"error":"email is not valid"}), 400
    if not usernameNotRepetitious(mongo, username):
        return jsonify({"error": "username is repitious"}), 400
    mongo.db.users.insert_one({
        "username": username,
        "city":city,
        "password": Hash(password),
        "email": email,
        "role": role
    })
    token = Generate_token(mongo)
    mongo.db.tokens.insert_one({"token": token, "username": username})
    return jsonify({"token":token})

@app.route('/login', methods=['POST'])
def login():
    username = str(request.form["username"])
    password = str(request.form["password"])
    tokens = list(mongo.db.tokens.find({"username": username}))
    if len(tokens) == 1 and list(mongo.db.users.find({"username": username}))[0]["password"] == Hash(password):
        return jsonify({"token":tokens[0]["token"]}), 200
    else:
        return jsonify({"error":"password is not valid"}), 400

@app.route("/upload/image", methods=["POST"])
def UplaodImage():
    File = request.files["image"]
    filename = secure_filename(File.filename)
    mongo.save_file(filename, File)
    return jsonify({"filename":filename})

@app.route("/submit/food", methods=["POST"])
def SubmitFood():
    token = request.form["token"]
    username = request.form["username"]
    QueryToken = list(mongo.db.tokens.find({"token":token}))
    if QueryToken[0]["username"] == username:
        mongo.db.foods.insert_one({
            "restaurant": str(username),
            "name": str(request.form["name"]),
            "description": str(request.form["desc"]),
            "price": str(request.form["price"]),
            "image": str(request.form["image_filename"]),
            "date": datetime.now()
        })
        return jsonify({"status":"done"})

@app.route("/q/restaurants")
def QueryRestaurant():
    restset = list(mongo.db.users.find({"role":"restaurant"}))
    for item in restset:
        item.pop("password")
        item.pop("email")
    return jsonify(list(restset))

@app.route("/q/foodbyRTi")
def GetfoodByName():
    restaurant = request.form["restaurant"]
    QueryFoods = mongo.db.foods.find({"restaurant": restaurant})
    foods = list(QueryFoods)
    if len(foods) == 0:
        return jsonify({"status":"there is no food"})
    else:
        return jsonify(foods)

#TODO: have food by popularity 


@app.route("/q/comments", methods=["GET"])
def GetComments():
    foodname = request.form["foodname"]
    restaurant = request.form["restaurant"]
    QueryComments = list(mongo.db.comments.find({
        "foodName": foodname,
        "restaurant":restaurant
    }))
    return jsonify(QueryComments), 200

@app.route("/q/image")
def GetImages():
    filename = request.form["filename"]
    return mongo.send_file(str(filename))

@app.route("/submit/comment", methods=["POST"])
def SubmitComment():
    token = request.form["token"]
    username = request.form["username"]
    QueryToken = list(mongo.db.tokens.find({"token":token}))
    if QueryToken[0]["username"] == username:
        commentMsg = request.form["comment"]
        restaurant = request.form["restaurant"]
        name = request.form["name"]
        QueryFood = mongo.db.foods.find({"name":name, "restaurant":restaurant})
        if not len(list(QueryFood)) == 0:
            mongo.db.comments.insert_one({
                "foodName": name,
                "restaurant": restaurant,
                "username": username,
                "comment": commentMsg
            })
            return jsonify({"status":"done"})
        else:
            return jsonify({"error", "food not found"}), 404
    else:
        return jsonify({"error": "your token is invalid"}), 406

@app.route("/vote/food", methods=["POST"])
def VoteFood():
    restaurant = request.form["restaurant"]
    foodname = request.form["food"]
    token = request.form["token"]
    username = request.form["username"]
    QueryToken = list(mongo.db.tokens.find({"token":token}))
    repitiousComment = mongo.db.votes.find({"restaurant": restaurant,"name": foodname, "username": username})
    if not QueryToken[0]["username"] == username:
        return jsonify({"error":"invalid token"}), 400
    if len(list(repitiousComment)) > 0:
        return jsonify({"error": "repitious voting"}), 403
    QueryFood = list(mongo.db.foods.find({
        "restaurant" : restaurant,
        "name": foodname
    }))

    if len(QueryFood) == 0 or len(QueryFood) > 2:
        return {"error":"no such food!!"}, 400

    mongo.db.votes.insert({"restaurant": restaurant,"name": foodname,"username": username,"dir": request.form["dir"]
    })
    return jsonify({"done":"submitted"})


@app.route("/q/votes")
def QueryVotes():
    food = request.form["food"]
    restaurant = request.form["restaurant"]
    posQuery = mongo.db.votes.find({"restaurant": restaurant,"name": food,"dir": "up"})
    negQuery = mongo.db.votes.find({"restaurant": restaurant,"name": food,"dir": "down"})
    totalVotes = len(list(posQuery)) - len(list(negQuery))
    print(list(posQuery))
    return jsonify({"total": str(totalVotes)})

@app.route("/q/restbycity")
def QRestByCities():
    city = request.form["city"]
    city = str(city).lower()
    queryset = list(mongo.db.users.find({"role":"restaurant", "city": city}))
    for item in queryset:
        item.pop("password")
        item.pop("email")
    print(queryset)
    return jsonify(queryset)



if __name__ == "__main__":
    app.run("0.0.0.0", 5000, debug=True) 
