from fastapi import FastAPI, HTTPException
from fastapi import Request

from db_mongodb.schema import  users_serializer
from db_mongodb.db import user_collection
from db_mongodb.model import User

import time
import jwt

import os
from dotenv import load_dotenv

### Loads the env variables
load_dotenv()

### Checks for users in the DB with the given email amd password and returns the user if found
def login_valid(email, password)->User|None:
    try:
        users = users_serializer(user_collection.find())
        for user in users:
            if user['email'] == email and user['password'] == password:
                return user
        return None 
    except Exception as error:
         raise HTTPException(status_code=404, detail= str(error))
    
    
### Creates payload using user id and session expire time and generates token for the payload using jwt encode and returns the token     
def sign_jwt(user_id: str) -> str:
    try:
        payload = {
            "user_id": user_id,
            "expires": time.time() + float(os.getenv('SESSION_EXPIRE_TIME'))
        }

        jwt_code = os.getenv('JWT_CODE')
        jwt_algorithm = os.getenv('JWT_ALGORITHM')

        token = jwt.encode(payload, jwt_code, algorithm= jwt_algorithm)  

        return token
    
    except Exception as error:
         raise HTTPException(status_code=404, detail= str(error))
    
         
### Gets the token from cookies and decode it with jwt decode. Checks for expiry time and user id and returns value accordingly
def decode_jwt(request: Request,login_user: User) -> bool:
    try:
        token = request.cookies.get("access_token")
        jwt_code = os.getenv('JWT_CODE')
        jwt_algorithm = os.getenv('JWT_ALGORITHM')

        decoded_token = jwt.decode(token, jwt_code, algorithms=[jwt_algorithm])

        if (decoded_token["expires"] >= time.time() and login_user["email"] == decoded_token["user_id"]): 
            return True
        else:
            return False
        
    except Exception as error:
         raise HTTPException(status_code=404, detail= str(error))

         