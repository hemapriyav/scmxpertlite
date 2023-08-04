from db_mongodb.schema import  users_serializer
from fastapi import FastAPI, HTTPException
from db_mongodb.db import collection_name
from db_mongodb.model import User
from fastapi import Request

import time
import jwt

def login_valid(email, password)->User|None:
    try:
        users = users_serializer(collection_name.find())
        for user in users:
            print(user)
            if user['email'] == email and user['password'] == password:
                return user
        return None 
    except Exception as error:
         raise HTTPException(status_code=404, detail= str(error))

def sign_jwt(user_id: str) -> str:
    try:
        payload = {
            "user_id": user_id,
            "expires": time.time() + 600
        }
        token = jwt.encode(payload, "code", algorithm="HS256")
        return token
    except Exception as error:
         raise HTTPException(status_code=404, detail= str(error))
         

def decode_jwt(request: Request,login_user: User) -> dict | None:
    print("inside decodeJWT")
    print("access token from request-"+str(request.cookies.get("access_token")))
    try:
        token = request.cookies.get("access_token")
        decoded_token = jwt.decode(token, "code", algorithms=["HS256"])
        print(decoded_token)
        
        print("before login user check-") 
        print(login_user)
        print("loginuser email-"+  str(login_user["email"]))
        if (decoded_token["expires"] >= time.time() and login_user["email"] == decoded_token["user_id"]): 
            print("inside if loop decodejwt")
            return decoded_token 
        else:
            print("inside else decodejwt")
            return None
    except Exception as error:
         raise HTTPException(status_code=404, detail= str(error))

         