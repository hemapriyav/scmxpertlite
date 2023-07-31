from typing import Union

from fastapi import FastAPI, HTTPException

from fastapi.templating import Jinja2Templates  

from fastapi import APIRouter

from fastapi import Request, Response, Form, Body

from fastapi.staticfiles import StaticFiles

from fastapi.responses import HTMLResponse

import time
from typing import Dict
import jwt
from datetime import date,timedelta
import random,string

from validation import credential_valid,email_valid

from db_mongodb.db import collection_name, collection_name2,collection_name3
from db_mongodb.schema import  users_serializer,shipments_serializer,device_datas_serializer
from db_mongodb.model import User, Shipment

import smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False) 

app = FastAPI()  

app.mount("/static", StaticFiles(directory="static"), name="static")

loginUser = None

REGISTER_PAGE = "/register.html"
LOGIN_PAGE = "/login.html"
LOGOUT_PAGE = "/logout.html"
CHG_PWD_PAGE = "/changepassword.html"
MSG_LOGIN = "Please Login to continue"
MSG_SESSION_EXIPRED = "Session Expired"

############Register/Sign Up methods #################
@app.get("/register/")
def register_get(request: Request):
    return templates.TemplateResponse(REGISTER_PAGE,{"request": request})  

@app.post("/register/")
def register_post(request: Request,username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    try:
        errors: list =  credential_valid(username,email,password)
        print(errors)
        if len(errors) > 0 :
            print("inside error")
            return templates.TemplateResponse(REGISTER_PAGE,{"request": request, "errors": errors,"username": username,"email": email,"password": password})
        print("before getting users from db")
        users = users_serializer(collection_name.find())
        print("users - "+ str(users))
        for user in users:
            print(user)
            if user['email'] == email:
                    # raise HTTPException(status_code=404, detail="user already exists")
                    return templates.TemplateResponse(REGISTER_PAGE,{"request": request,"errors": ["User already exists"],"username": username,"email": email,"password": password})  
        print("before create user call")
        usr =create_user(User(name= username, email= email, password= password,role= "User"))
        print(usr)
        users = users_serializer(collection_name.find())
        print(users)
        return templates.TemplateResponse(REGISTER_PAGE,{"request": request, "message": "Signed Up Successfully"})  
    except Exception as error:
         raise HTTPException(status_code=404, detail= str(error))
         
############ Login methods #################
@app.get("/login/")
def login_get(request: Request):
    return templates.TemplateResponse(LOGIN_PAGE,{"request": request})  

@app.post("/login/")
def login_post(response: Response, request: Request, email: str = Form(...), password: str = Form(...)):
    try:
        error = email_valid(email)
        if error is not None:
                errors = []
                errors.append(error)
                return templates.TemplateResponse(LOGIN_PAGE,{"request": request, "errors": errors,"email": email,"password": password})  
        users = users_serializer(collection_name.find())
        for user in users:
            print(user)
            if user['email'] == email and user['password'] == password:
                token =sign_jwt(email)
                print(token)
                response.set_cookie(key="access_token", value = token, httponly=True)
                print("after signJWT")
                global loginUser 
                loginUser = user
                print(loginUser) 
                shipments = get_shipment()
                print(shipments)
                response = templates.TemplateResponse("/dashboard.html",{"request": request, "user": loginUser, "shipment": shipments})  
                response.set_cookie(key="access_token", value = token, httponly=True)
                return response
        errors=["invalid email or password"]       
        return templates.TemplateResponse(LOGIN_PAGE,{"request": request, "errors": errors,"email": email,"password": password})  
    except Exception as error:
         raise HTTPException(status_code=404, detail= str(error))
         

######### Logout methods###########
@app.get("/logout")
def logout_get(request: Request):
    global loginUser
    loginUser= None
    response = templates.TemplateResponse(LOGOUT_PAGE,{"request": request, "message":"Thank You"})
    response.delete_cookie("access_token")
    return response

######### Shipment methods###########
@app.get("/shipment")
def shipment_get(request: Request):
    try:
        global loginUser
        if loginUser is None:
            return templates.TemplateResponse(LOGOUT_PAGE,{"request": request, "message":MSG_LOGIN}) 
        decoded_user =decode_jwt(request)
        print("decodedUser-"+str(decoded_user))
        if(decoded_user is None):
            return templates.TemplateResponse(LOGOUT_PAGE,{"request": request,"message":MSG_SESSION_EXIPRED}) 
        print(date.today())
        min_date = date.today()+ timedelta(days=1)
        print(min_date)
        device_id = ["1150","1151","1152","1153","1154","1155","1156","1157","1158"]
        return templates.TemplateResponse("/shipment.html",{"request": request, "deviceId": device_id,"expDel": min_date, "min_date": min_date}) 
    except Exception as error:
         raise HTTPException(status_code=404, detail= str(error))
         
    
@app.post("/shipment")
async def shipment_post(request: Request):
    try:
        global loginUser
        if loginUser is None:
            return templates.TemplateResponse(LOGOUT_PAGE,{"request": request, "message":MSG_LOGIN}) 
        decoded_user =decode_jwt(request)
        print("decodedUser-"+str(decoded_user))
        if(decoded_user is None):
            return templates.TemplateResponse(LOGOUT_PAGE,{"request": request,"message":MSG_SESSION_EXIPRED}) 
        shipment = await request.form()
        print (shipment)
        print(loginUser)
        last_ship_num= shipments_serializer(collection_name2.find().sort("shipNum",-1).limit(1))
        ship_num=1
        if(len(last_ship_num)>0):
            print(last_ship_num[0]["shipNum"])
            ship_num =last_ship_num[0]["shipNum"] +1
            print(ship_num)
        print("after if -"+str(ship_num))
        shipment_new =create_shipment(Shipment(
            shipNum = ship_num,
            contNum= shipment['contNum'],
            route= shipment['routeDtl'],
            goodsType= shipment['goodsType'], 
            device= shipment['device'],
            delDate= shipment['expDel'],
            poNum= shipment['poNum'], 
            delNum= shipment['delNum'],
            ndcNum= shipment['ndcNum'],
            batchId= shipment['batchId'],
            serialNum= shipment['serialNum'], 
            shipDesc= shipment['shipDesc'],
            userId= loginUser['id']
        ))
        print(shipment_new[0]["shipNum"])
        return templates.TemplateResponse("/shpcreated.html",{"request": request,"shipNum": shipment_new[0]["shipNum"]})
    except Exception as error:
         raise HTTPException(status_code=404, detail= str(error))
         
    
@app.get("/shpcreated")
def shpcreated_get(request: Request):
    return templates.TemplateResponse("/shpcreated.html",{"request": request}) 

######### Datastream methods #############
@app.get("/datastream/{ship_num}")
def datastream_get(request: Request,ship_num:int):
    try:
        global loginUser
        if loginUser is None:
            return templates.TemplateResponse(LOGOUT_PAGE,{"request": request, "message":MSG_LOGIN}) 
        decoded_user =decode_jwt(request)
        print("decodedUser-"+str(decoded_user))
        if(decoded_user is None):
            return templates.TemplateResponse("/.html",{"request": request,"message":MSG_SESSION_EXIPRED})
        print("inside datastream with shipnum-"+ str(ship_num))
        shipment= shipments_serializer(collection_name2.find({"shipNum": ship_num}))
        print(shipment[0]["device"])
        device_data = device_datas_serializer(collection_name3.find({"Device_ID": int(shipment[0]['device'])}))
        for data in device_data:
            print(data)
        return templates.TemplateResponse("/datastream.html",{"request": request, "deviceData": device_data,"shipment":shipment[0]}) 
    except Exception as error:
         raise HTTPException(status_code=404, detail= str(error))
         
    
############## Dashboard/Home methods #################
@app.get("/dashboard") 
def dashboard_get(request: Request):
    try:
        global loginUser
        if loginUser is None:
            return templates.TemplateResponse(LOGOUT_PAGE,{"request": request, "message":MSG_LOGIN}) 
        decoded_user =decode_jwt(request)
        print("decodedUser-"+str(decoded_user))
        if(decoded_user is None):
            return templates.TemplateResponse(LOGOUT_PAGE,{"request": request,"message":MSG_SESSION_EXIPRED}) 
        shipments = get_shipment() 
        print(loginUser)
        return templates.TemplateResponse("/dashboard.html",{"request": request, "user": loginUser, "shipment": shipments})  
    except Exception as error:
         raise HTTPException(status_code=404, detail= str(error))
         
    
 ############# Forgot Password methods ##################
@app.get("/forgotPassword")
def forgot_pwd_get(request: Request):
   return templates.TemplateResponse("/forgotPassword.html",{"request": request}) 
    
    
@app.post("/forgotPassword")
def forgot_pwd_post(request: Request,email: str = Form(...)): 
    try: 
        print("inside sendemail")
        print(email)
        errors =  email_valid(email)
        print(errors)
        if errors is not None:
            print("inside not error")
            return templates.TemplateResponse("/forgotPassword.html",{"request": request, "errors": [errors],"email": email})
        print("success")
        password = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        print("password-"+password)
        generate_auth_email(password,email)
        collection_name.find_one_and_update( { 'email': email}, { '$set': { 'password': password} } ) 
        return templates.TemplateResponse(LOGOUT_PAGE,{"request": request,"message":"Password sent successfully to the email id.Please change the password after login"}) 
    except Exception as error:
         raise HTTPException(status_code=404, detail= str(error))
         

############ Change Password methods ###################
@app.get("/changepassword")
def chg_pwd_get(request: Request):
    try:
        global loginUser
        if loginUser is None:
             return templates.TemplateResponse(LOGOUT_PAGE,{"request": request, "message":MSG_LOGIN}) 
        decoded_user =decode_jwt(request)
        print("decodedUser-"+str(decoded_user))
        if(decoded_user is None):
            return templates.TemplateResponse(LOGOUT_PAGE,{"request": request,"message":MSG_SESSION_EXIPRED}) 
        return templates.TemplateResponse(CHG_PWD_PAGE,{"request": request})  
    except Exception as error:
         raise HTTPException(status_code=404, detail= str(error))
         
    
@app.post("/changepassword")
def chg_pwd_post(request: Request,currentpwd: str = Form(...),newpwd:str = Form(...)):
    try:
        global loginUser
        if loginUser is None:
             return templates.TemplateResponse(LOGOUT_PAGE,{"request": request, "message":MSG_LOGIN}) 
        decoded_user =decode_jwt(request)
        print("decodedUser-"+str(decoded_user))
        if(decoded_user is None):
            return templates.TemplateResponse(LOGOUT_PAGE,{"request": request,"message":MSG_SESSION_EXIPRED}) 
        if(currentpwd == loginUser['password']):
            if currentpwd != newpwd:
                collection_name.find_one_and_update( { 'email': loginUser['email']}, { '$set': { 'password': newpwd}})
            else:
                return templates.TemplateResponse(CHG_PWD_PAGE,{"request": request, "error": "New Password cannot be same as current password","currentpwd": currentpwd, "newpwd":newpwd})
        else:
             return templates.TemplateResponse(CHG_PWD_PAGE,{"request": request, "error": "invalid current password","currentpwd": currentpwd, "newpwd":newpwd})

        return templates.TemplateResponse(CHG_PWD_PAGE,{"request": request,"message": "Password changed Successfully"})  
    except Exception as error:
         raise HTTPException(status_code=404, detail= str(error))
         

###### Internal Functions ##########
def get_shipment():
    try:
        global loginUser
        if(loginUser["role"] == "admin"):
            shipments = shipments_serializer(collection_name2.find())
        else:    
            shipments = shipments_serializer(collection_name2.find({"userId": loginUser['id']}))
        print(shipments)
        return shipments
    except Exception as error:
         raise HTTPException(status_code=404, detail= str(error))
         

def create_user(user: User):
    try:
        _id = collection_name.insert_one(dict(user))
        return users_serializer(collection_name.find({"_id": _id.inserted_id}))
    except Exception as error:
         raise HTTPException(status_code=404, detail= str(error))
         

def create_shipment(shipment: Shipment):
    try:
        _id = collection_name2.insert_one(dict(shipment))
        return shipments_serializer(collection_name2.find({"_id": _id.inserted_id}))
    except Exception as error:
         raise HTTPException(status_code=404, detail= str(error))
         

# function used for signing the JWT string
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
         

def decode_jwt(request: Request) -> dict | None:
    print("inside decodeJWT")
    print("access token from request-"+str(request.cookies.get("access_token")))
    try:
        token = request.cookies.get("access_token")
        decoded_token = jwt.decode(token, "code", algorithms=["HS256"])
        print(decoded_token)
        global loginUser 
        print("before login user check-") 
        print(loginUser)
        print("loginuser email-"+  str(loginUser["email"]))
        if (decoded_token["expires"] >= time.time() and loginUser["email"] == decoded_token["user_id"]): 
            print("inside if loop decodejwt")
            return decoded_token 
        else:
            print("inside else decodejwt")
            return None
    except Exception as error:
         raise HTTPException(status_code=404, detail= str(error))
         

def generate_auth_email(passcode: str,receiver_mail: str):
    try:
        print("inside generate auth email")
        subject = "scmxpertlite password"
        body ="\nHi,\n\n Your Password is "+str(passcode)
        sender_email="scmxpert1@gmail.com"
        receiver_email = receiver_mail
        password="mlyjkttmugfhcigo"

        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = ", ".join(receiver_email)
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))
        text = message.as_string()

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            print("before login-"+str(sender_email)+","+str(password))
            server.login(sender_email, password)
            print("before send mail-"+str(text))
            server.sendmail(sender_email, receiver_email, text)
        print("end of generate auth email")

    except Exception as error:
         raise HTTPException(status_code=404, detail= str(error))
         






  
