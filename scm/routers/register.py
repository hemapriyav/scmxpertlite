from db_mongodb.schema import  users_serializer
from fastapi import HTTPException
from db_mongodb.db import collection_name
from db_mongodb.model import User

def register_valid(email):
    try:
        users = users_serializer(collection_name.find())
        print("users - "+ str(users))
        for user in users:
            print(user)
            if user['email'] == email:
                    return False
        print("before return true")
        return True
    except Exception as error:
         raise HTTPException(status_code=404, detail= str(error))
    
def create_user(user: User):
    try:
        print("inside create user")
        _id = collection_name.insert_one(dict(user))
        return users_serializer(collection_name.find({"_id": _id.inserted_id}))
    except Exception as error:
         raise HTTPException(status_code=404, detail= str(error))