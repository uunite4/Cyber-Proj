import json

DB_PATH = "userDB.json"

def getAll():
    with open(DB_PATH) as file:
        data = json.load(file)
        return data

def writeUser(user):
    allDB = getAll()
    allDB["users"].append(user)

    with open(DB_PATH, "w") as file:
        json.dump(allDB, file, indent=4)

