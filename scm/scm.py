from typing import Union

from fastapi import FastAPI, HTTPException

from fastapi.templating import Jinja2Templates  

from fastapi import APIRouter

from fastapi import Request, Response, Form, Body

from fastapi.staticfiles import StaticFiles

from fastapi.responses import HTMLResponse

from validation import credential_valid,email_valid


import time
from typing import Dict

import jwt


from db_mongodb.db import collection_name, collection_name2,collection_name3

from db_mongodb.schema import user_serializer, users_serializer, shipment_serializer, shipments_serializer,device_data_serializer,device_datas_serializer
from db_mongodb.model import User, Shipment

from bson import ObjectId

import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from datetime import date,timedelta

import random,string


templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False) 

app = FastAPI()  

app.mount("/static", StaticFiles(directory="static"), name="static")

loginUser = None


 


@app.get("/register/")
def register(request: Request):

    return templates.TemplateResponse("/register.html",{"request": request})  

@app.get("/login/")
def register(request: Request):
    return templates.TemplateResponse("/login.html",{"request": request})  

@app.get("/logout")
def logout(response: Response, request: Request):
    global loginUser
    loginUser= None
    response = templates.TemplateResponse("/logout.html",{"request": request, "message":"Thank You"})
    response.delete_cookie("access_token")
    return response
    # return templates.TemplateResponse("/logout.html",{"request": request, "message":"Thank You"})

@app.get("/shipment")
def register(request: Request):
    global loginUser
    if loginUser is None:
        return templates.TemplateResponse("/logout.html",{"request": request, "message":"Please Login to continue"}) 
    decodedUser =decodeJWT(request,"token")
    print("decodedUser-"+str(decodedUser))
    if(decodedUser is None):
        return templates.TemplateResponse("/logout.html",{"request": request,"message":"Session Expired"}) 
    # current_date = datetime.datetime.now()
    # min_date= str(current_date.year)+"-"+str(current_date.month)+"-"+str(current_date.day + 1)
    print(date.today())
    min_date = date.today()+ timedelta(days=1)
    print(min_date)
    device_id = ["1150","1151","1152","1153","1154","1155","1156","1157","1158"]
    return templates.TemplateResponse("/shipment.html",{"request": request, "deviceId": device_id,"expDel": min_date, "min_date": min_date}) 

@app.get("/datastream/{shipNum}")
def register(request: Request,shipNum:int):
    global loginUser
    if loginUser is None:
        return templates.TemplateResponse("/logout.html",{"request": request, "message":"Please Login to continue"}) 
    decodedUser =decodeJWT(request,"token")
    print("decodedUser-"+str(decodedUser))
    if(decodedUser is None):
        return templates.TemplateResponse("/.html",{"request": request,"message":"Session Expired"})
    print("inside datastream with shipnum-"+ str(shipNum))
    shipment= shipments_serializer(collection_name2.find({"shipNum": shipNum}))
    print(shipment[0]["device"])
    deviceData = device_datas_serializer(collection_name3.find({"Device_ID": int(shipment[0]['device'])}))
    for data in deviceData:
        print(data)
    return templates.TemplateResponse("/datastream.html",{"request": request, "deviceData": deviceData,"shipment":shipment}) 

    return      

# @app.get("/datastream")
# def register(request: Request):
#     global loginUser
#     if loginUser is None:
#         return templates.TemplateResponse("/logout.html",{"request": request, "message":"Please Login to continue"}) 
#     decodedUser =decodeJWT(request,"token")
#     print("decodedUser-"+str(decodedUser))
#     if(decodedUser is None):
#         return templates.TemplateResponse("/.html",{"request": request,"message":"Session Expired"}) 
#     deviceData = device_datas_serializer(collection_name3.find())
#     for data in deviceData:
#         print(data)
#     return templates.TemplateResponse("/datastream.html",{"request": request, "deviceData": deviceData}) 

#To be removed - used for testing
# @app.get("/dashboard") 
# def register(request: Request):
#     global loginUser
#     shipments = get_shipment()
#     return templates.TemplateResponse("/dashboard.html",{"request": request, "userName": loginUser['name'], "shipment": shipments})  

@app.get("/dashboard") 
def register(request: Request):
    global loginUser
    if loginUser is None:
        return templates.TemplateResponse("/logout.html",{"request": request, "message":"Please Login to continue"}) 
    decodedUser =decodeJWT(request,"token")
    print("decodedUser-"+str(decodedUser))
    if(decodedUser is None):
        return templates.TemplateResponse("/logout.html",{"request": request,"message":"Session Expired"}) 
    # if(decodedUser['login']):
    #      return templates.TemplateResponse("/login.html",{"request": request})
    shipments = get_shipment()
    return templates.TemplateResponse("/dashboard.html",{"request": request, "userName": loginUser['name'], "shipment": shipments})  

@app.get("/forgotPassword")
def register(request: Request):

    return templates.TemplateResponse("/forgotPassword.html",{"request": request})  

@app.post("/forgotPassword")
def sendEmail(request: Request,email: str = Form(...)):
    
    print("inside sendemail")
    # print(str(request.json))
    # email: dict = Body(...) 
    print(email)
    errors =  email_valid(email)
    print(errors)
    if errors is not None:
        print("inside not error")
        return templates.TemplateResponse("/forgotPassword.html",{"request": request, "errors": [errors],"email": email})
    print("success")
    password = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    print("password-"+password)
    # password='123456'
    generate_auth_email(password,email)
    # collection_name.updateOne( { title: "Post Title 1" }, { $set: { likes:  } } ) 
    collection_name.find_one_and_update( { 'email': email}, { '$set': { 'password': password} } ) 
    return templates.TemplateResponse("/logout.html",{"request": request,"message":"Password sent successfully.Please change the password after login"}) 


@app.post("/register/")
def register(request: Request,username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    errors: list =  credential_valid(username,email,password)
    print(errors)
    if len(errors) > 0 :
        print("inside not error")
        return templates.TemplateResponse("/register.html",{"request": request, "errors": errors})
    print("before getting users from db")
    users = users_serializer(collection_name.find())
    print("users - "+ str(users))
    for user in users:
        print(user)
        if user['email'] == email:
                # raise HTTPException(status_code=404, detail="user already exists", headers= {"X-Error": "there is an error"},)
                 return templates.TemplateResponse("/register.html",{"request": request,"errors": ["User already exists"]})  
    print("before create user call")
    usr =create_user(User(name= username, email= email, password= password,role= "User"))
    print(usr)
    users = users_serializer(collection_name.find())
    print(users)
    return templates.TemplateResponse("/register.html",{"request": request, "message": "Signed Up Successfully"})  
   # return HTMLResponse("<b>Signed Up Successfully</b>")

   # return signJWT(email)
    #return {"email": email, "username": username, "password": password}



@app.post("/login/")
def login(response: Response, request: Request, email: str = Form(...), password: str = Form(...)):
#def register(user: User):
    error = email_valid(email)
    if error is not None:
            errors = []
            errors.append(error)
            return templates.TemplateResponse("/login.html",{"request": request, "errors": errors})  
    users = users_serializer(collection_name.find())

    for user in users:
        print(user)
        if user['email'] == email and user['password'] == password:
            token =signJWT(email)
            print(token)
            response.set_cookie(key="access_token", value = token, httponly=True)
            #request.session["access_token"] = token
            ####### code to be moved to separate function
            #print(request.cookies.get("access_token"))
            # print(jwt.decode(token, 'code', algorithms=['HS256']))
           
           
            # decodedUser =decodeJWT(request,token)
            # print("decodedUser-"+str(decodedUser))
            # if decodedUser is None:
            #     print("token expired")
            #####################end - code to be moved to separate function##################33 
            print("after signJWT")
            global loginUser 
            loginUser = user
            print(loginUser) 
            # shipments = shipments_serializer(collection_name2.find({"userId": user['id']}))
            shipments = get_shipment()
            print(shipments)
            response = templates.TemplateResponse("/dashboard.html",{"request": request, "userName": user['name'], "shipment": shipments})  
            response.set_cookie(key="access_token", value = token, httponly=True)
            return response
            #return templates.TemplateResponse("/dashboard.html",{"request": request, "response": response,"userName": user['name'], "shipment": shipments})  

            #return signJWT(email)
    errors=["invalid email or password"]       
    return templates.TemplateResponse("/login.html",{"request": request, "errors": errors})  

@app.post("/shipment")
async def create_shipment(request: Request):
    global loginUser
    if loginUser is None:
        return templates.TemplateResponse("/logout.html",{"request": request, "message":"Please Login to continue"}) 
    decodedUser =decodeJWT(request,"token")
    print("decodedUser-"+str(decodedUser))
    if(decodedUser is None):
        return templates.TemplateResponse("/logout.html",{"request": request,"message":"Session Expired"}) 
    shipment = await request.form()
    payload: dict = Body(...)
    print (shipment)
    print(shipment['shipNum'])
    print(loginUser)
    last_ship_num= shipments_serializer(collection_name2.find().sort("shipNum",-1).limit(1))
    shipNum=1
    if(len(last_ship_num)>0):
        print(last_ship_num[0]["shipNum"])
        shipNum =last_ship_num[0]["shipNum"] +1
        print(shipNum)
    print("after if -"+str(shipNum))
    shipmentNew =create_shipment(Shipment(
        # shipNum= shipment['shipNum'], 
        shipNum = shipNum,
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

def get_shipment():
     global loginUser
     if(loginUser["role"] == "Admin"):
         shipments = shipments_serializer(collection_name2.find())
     else:    
        shipments = shipments_serializer(collection_name2.find({"userId": loginUser['id']}))
     print(shipments)
     return shipments

def create_user(user: User):

    _id = collection_name.insert_one(dict(user))
    return users_serializer(collection_name.find({"_id": _id.inserted_id}))

def create_shipment(shipment: Shipment):
    _id = collection_name2.insert_one(dict(shipment))
    return shipments_serializer(collection_name2.find({"_id": _id.inserted_id}))

# function used for signing the JWT string
def signJWT(user_id: str) -> str:
    payload = {
        "user_id": user_id,
        "expires": time.time() + 600
    }
    token = jwt.encode(payload, "code", algorithm="HS256")
    return token

def decodeJWT(request: Request,token: str) -> dict:
    print("inside decodeJWT")
    print("access token from request-"+str(request.cookies.get("access_token")))
    try:
        token = request.cookies.get("access_token")
        decoded_token = jwt.decode(token, "code", algorithms=["HS256"])
        print(decoded_token)
        global loginUser 
        print("before login user check-") 
       
        # if loginUser is None:
        #     print("inside not login user") 
        #     return {"login": "login"}
        print(loginUser)
        print("loginuser email-"+  str(loginUser["email"]))
        if (decoded_token["expires"] >= time.time() and loginUser["email"] == decoded_token["user_id"]): 
            print("inside if loop decodejwt")
            return decoded_token 
        else:
            print("inside else decodejwt")
            return None
    ##### also need to check if user id is same as loged in user ##########
    except:
        print("inside except decodejwt")
        return {"error": "error"}

########### Hands on functions ##############

def generate_auth_email(passcode: str,RECEIVER_EMAIL: str):
    print("inside generate auth email")
    subject = "Verification Code"
    body ="\nHi Everyone,\n\n Your verification code is "+str(passcode)
    #sender_email = config.EMAIL_ID
    sender_email="scmxpert1@gmail.com"
    receiver_email = RECEIVER_EMAIL
    #password = config.EMAIL_PWD
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
@app.get("/")

def read_root():

    return {"Hello": "World"}




@app.get("/items/{item_id}")

def read_item(item_id: int, q: Union[str, None] = None):

    return {"item_id": item_id, "q": q}

def getInteger():
    result = int(input("Enter integer: "))
    return result
  
def Main():
    print("Started")
  
    # calling the getInteger function and 
    # storing its returned value in the output variable
    output = getInteger()     
    var = 1
    print("entered number",output,var+2,"done")
  
# now we are required to tell Python 
# for 'Main' function existence
if __name__=="__main__":
    Main()