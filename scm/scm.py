

from fastapi import FastAPI, HTTPException
from fastapi.templating import Jinja2Templates  
# from fastapi import APIRouter
from fastapi import Request, Response, Form
from fastapi.staticfiles import StaticFiles

from datetime import date,timedelta

from validation import credential_valid,email_valid

from db_mongodb.model import User

from routers.register import register_valid,create_user
from routers.login import login_valid,sign_jwt,decode_jwt
from routers.shipment import shipment_create,get_shipment,get_shipment_shipnum,get_device_data
from routers.password import generate_auth_email,changepwd

templates = Jinja2Templates(directory="templates")
# router = APIRouter(include_in_schema=False) 

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
        valid = register_valid(email)  
        print("valid-"+str(valid))
        if not valid:
            print("inside user already exists")
            return templates.TemplateResponse(REGISTER_PAGE,{"request": request,"errors": ["User already exists"],"username": username,"email": email,"password": password})  
        print("before create user call")
        usr =create_user(User(name= username, email= email, password= password,role= "User"))
        print(usr)
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
        user = login_valid(email,password)
        if(user is not None):
                token =sign_jwt(email)
                print(token)
                response.set_cookie(key="access_token", value = token, httponly=True)
                print("after signJWT")
                global loginUser 
                loginUser = user
                print(loginUser) 
                shipments = get_shipment(loginUser)
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
        decoded_user =decode_jwt(request,loginUser)
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
        decoded_user =decode_jwt(request,loginUser)
        print("decodedUser-"+str(decoded_user))
        if(decoded_user is None):
            return templates.TemplateResponse(LOGOUT_PAGE,{"request": request,"message":MSG_SESSION_EXIPRED}) 
        shipment = await request.form()
        ship_num= await shipment_create(shipment,loginUser['id'])
        return templates.TemplateResponse("/shpcreated.html",{"request": request,"shipNum": ship_num})
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
        decoded_user =decode_jwt(request,loginUser)
        print("decodedUser-"+str(decoded_user))
        if(decoded_user is None):
            return templates.TemplateResponse(LOGOUT_PAGE,{"request": request,"message":MSG_SESSION_EXIPRED})
        print("inside datastream with shipnum-"+ str(ship_num))
        shipment = get_shipment_shipnum(ship_num)
        print(shipment[0]["device"])
        device_data =get_device_data(shipment[0]["device"])
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
        decoded_user =decode_jwt(request,loginUser)
        print("decodedUser-"+str(decoded_user))
        if(decoded_user is None):
            return templates.TemplateResponse(LOGOUT_PAGE,{"request": request,"message":MSG_SESSION_EXIPRED}) 
        shipments = get_shipment(loginUser) 
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
        generate_auth_email(email)
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
        decoded_user =decode_jwt(request,loginUser)
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
        decoded_user =decode_jwt(request,loginUser)
        print("decodedUser-"+str(decoded_user))
        if(decoded_user is None):
            return templates.TemplateResponse(LOGOUT_PAGE,{"request": request,"message":MSG_SESSION_EXIPRED}) 
        if(currentpwd == loginUser['password']):
            if currentpwd != newpwd:
                changepwd( loginUser['email'],newpwd)
            else:
                return templates.TemplateResponse(CHG_PWD_PAGE,{"request": request, "error": "New Password cannot be same as current password","currentpwd": currentpwd, "newpwd":newpwd})
        else:
             return templates.TemplateResponse(CHG_PWD_PAGE,{"request": request, "error": "invalid current password","currentpwd": currentpwd, "newpwd":newpwd})

        return templates.TemplateResponse(CHG_PWD_PAGE,{"request": request,"message": "Password changed Successfully"})  
    except Exception as error:
         raise HTTPException(status_code=404, detail= str(error))
         






  
