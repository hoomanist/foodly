import random
import json
import hashlib
from bson import ObjectId
import re
from secrets import token_hex
from datetime import datetime

def Hash(string):
    result = hashlib.sha256(string.encode())
    return result.hexdigest()

def Generate_token(mongo):
    token = token_hex(256)
    if len(list(mongo.db.tokens.find({"token": token}))) == 0:
        return token
    else:
        Generate_token(mongo)

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return str(o)
        return json.JSONEncoder.default(self, o)

def usernameNotRepetitious(mongo, username):
    if len(list(mongo.db.users.find({"username": username}))) == 0:
        return True
    else:
        return False

def EmailValidation(email):
    regex =  "^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$"
    return re.search(regex, email)
