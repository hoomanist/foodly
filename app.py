from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from werkzeug.utils import secure_filename
from utils import Generate_token, JSONEncoder, Hash

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/foodly"
app.json_encoder = JSONEncoder
mongo = PyMongo(app)

@app.route("/register", methods=['POST'])
def register():
    username = request.args["username"]
    password = request.args["password"]
    phone = request.args["phone"]
    role = request.args["role"]
    if not role in ["customer", "restaurant"]:
        return jsonify({"error":"bad role"}), 403
    try:
        mongo.db.users.insert_one({
            "username": username,
            "password": Hash(password), 
            "phone": phone,
            "role": role
        })
    except writeError as e:
        return jsonify({"error":"error while writing data to database"}), 500 
    token = Generate_token(mongo)
    mongo.db.tokens.insert_one({"token": token, "username": username})
    return jsonify({"token":token})

@app.route('/login', methods=['POST'])
def login():
    username = str(request.args["username"])
    password = str(request.args["password"])
    tokens = list(mongo.db.tokens.find({"username": username}))
    if len(tokens) == 1 and list(mongo.db.users.find({"username": username}))[0]["password"] == Hash(password):
        return jsonify({"token":tokens[0]["token"]}), 200
    else:
        return jsonify({"error":"something went wrong"}), 403

@app.route("/upload/image", methods=["POST"])
def UplaodImage():
    File = request.files["image"]
    filename = secure_filename(File.filename)
    mongo.save_file(filename, File)
    return jsonify({"filename":filename})

@app.route("/submit/food", methods=["POST"])
def SubmitFood():
    token = request.args["token"]
    username = request.args["username"]
    QueryToken = list(mongo.db.tokens.find({"token": int(token)}))
    if QueryToken[0]["username"] == username:
        QueryFood = mongo.db.foods.insert_one({
            "restaurant": str(username),
            "name": str(request.args["name"]),
            "description": str(request.args["desc"]),
            "price": str(request.args["price"]),
            "image": str(request.args["image_filename"])
        })
        return jsonify({"status":"done"})

@app.route("/q/foodsbr")
def GetFoodsByRestaurant():
    restaurant = request.args["restaurant"]
    QueryFoods = list(mongo.db.foods.find({"restaurant": restaurant}))
    if len(QueryFoods) == 0:
        return jsonify({"status":"there is no food"})
    else:
        return jsonify(QueryFoods)

@app.route("/q/image")
def GetImages():
    filename = request.args["filename"]
    return mongo.send_file(str(filename))

@app.route("/submit/comment", methods=["POST"])
def SubmitComment():
    token = request.args["token"]
    username = request.args["username"]
    QueryToken = list(mongo.db.tokens.find({"token": int(token)}))
    print(QueryToken)
    if QueryToken[0]["username"] == username:
        commentMsg = request.args["comment"]
        restaurant = request.args["restaurant"]
        name = request.args["name"]
        QueryFood = mongo.db.foods.find({"name":name, "restaurant":restaurant})
        if not len(list(QueryFood)) == 0:
            mongo.db.comments.insert_one({
                "foodName": name,
                "restaurant": restaurant,
                "username": username,
                "comment": commentMsg
            }) #TODO:add voting for any comment
            return jsonify({"status":"done"})
        else:
            return jsonify({"error", "food not found"}), 406
    else:
        return jsonify({"error": "your token is invalid"})
if __name__ == "__main__":
    app.run("0.0.0.0", 5000, debug=True)
