from fastapi import HTTPException

from db_mongodb.schema import  users_serializer
from db_mongodb.db import collection_name
from db_mongodb.model import User

### Checks if the given email id is already present in DB
def register_valid(email):
    try:
        users = users_serializer(collection_name.find())

        for user in users:
            if user['email'] == email:
                    return False
        return True
    
    except Exception as error:
         raise HTTPException(status_code=404, detail= str(error))

### Creates the user in DB and returns the user along with the generated id    
def create_user(user: User):
    try:
        _id = collection_name.insert_one(dict(user))
        return users_serializer(collection_name.find({"_id": _id.inserted_id}))
    
    except Exception as error:
         raise HTTPException(status_code=404, detail= str(error))