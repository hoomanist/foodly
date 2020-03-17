import random
def Generate_token(mongo):
    token = random.randint(0,10000)
    if len(list(mongo.db.tokens.find({"token": token}))) == 0:
        return token
    else:
        Generate_token()

