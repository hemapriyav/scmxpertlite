

from fastapi import FastAPI, HTTPException
from fastapi.templating import Jinja2Templates  
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

app = FastAPI()  

app.mount("/static", StaticFiles(directory="static"), name="static")

loginUser = None

REGISTER_PAGE = "/register.html"
LOGIN_PAGE = "/login.html"
LOGOUT_PAGE = "/logout.html"
CHG_PWD_PAGE = "/changepassword.html"
MSG_LOGIN = "Please Login to continue"
MSG_SESSION_EXIPRED = "Session Expired"

############################################## Register/Sign Up methods ################################################################

### Renders the register page for the user to sign up

@app.get("/register/")
def register_get(request: Request):
    return templates.TemplateResponse(REGISTER_PAGE,{"request": request})  


### Calls functions to validates the credentials for correctness and to create the user in DB.Renders success message on successful sign up
### or error messages in case validation fails
@app.post("/register/")
def register_post(request: Request,username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    try:
        ### Calls credential_valid function to check correctness of the credentials and renders error messages if any
        errors: list =  credential_valid(username,email,password)
        if len(errors) > 0 :
            return templates.TemplateResponse(REGISTER_PAGE,{"request": request, "errors": errors,"username": username,"email": email,"password": password})
        
        ### Calls register_valid to check if email is not already in DB and renders error messages if any
        valid = register_valid(email)  
        if not valid:
            return templates.TemplateResponse(REGISTER_PAGE,{"request": request,"errors": ["User already exists"],"username": username,"email": email,"password": password})  
        
        ### Calls create_user function to create the user in DB
        create_user(User(name= username, email= email, password= password,role= "User"))
        
        ### Renders the success message on successful sign up
        return templates.TemplateResponse(REGISTER_PAGE,{"request": request, "message": "Signed Up Successfully"}) 
     
    except Exception as error:
         raise HTTPException(status_code=404, detail= str(error))
         

################################################ Login methods #####################################################################

### Renders the login page for the user to sign in
@app.get("/login/")
def login_get(request: Request):
    return templates.TemplateResponse(LOGIN_PAGE,{"request": request})  


### Calls functions to check the correctness of credentials and to generate the jwt token for the login session.
# Renders the dashboard with shipment details of the user
@app.post("/login/")
def login_post(request: Request, email: str = Form(...), password: str = Form(...)):
    try:
        ### Calls email_valid to validate the correctness of the mail id and renders error messages if any
        error = email_valid(email)
        if error is not None:
                errors = []
                errors.append(error)
                return templates.TemplateResponse(LOGIN_PAGE,{"request": request, "errors": errors,"email": email,"password": password})  
       
        ### Calls login_valid to check the email and password present in db and gets the respective user.Renders error messages if any
        user = login_valid(email,password)
        if(user is not None):
                response: Response
                ### Calls sign_jwt to generate jwt token with the user's email id
                token =sign_jwt(email)

                ### Sets the loginuser global variable to the logged in user
                global loginUser 
                loginUser = user
                
                ### Calls get_shipment to get the shipments for the logged in user
                shipments = get_shipment(loginUser)
               
                ### Renders the dashboard page with the shipment details
                
                response = templates.TemplateResponse("/dashboard.html",{"request": request, "user": loginUser, "shipment": shipments})  
                
                ### Sets the token generated in cookies
                response.set_cookie(key="access_token", value = token, httponly=True)
                
                return response
        
        ### Renders error message in case of invalid email/password
        errors=["invalid email or password"]       
        return templates.TemplateResponse(LOGIN_PAGE,{"request": request, "errors": errors,"email": email,"password": password})  
    
    except Exception as error:
         raise HTTPException(status_code=404, detail= str(error))
         

############################################# Logout methods ##########################################################################

### Clears the loginUser variable and deletes the token in cookies and then renders the logout page with approriate message
@app.get("/logout")
def logout_get(request: Request):
    global loginUser
    loginUser= None
    response = templates.TemplateResponse(LOGOUT_PAGE,{"request": request, "message":"Thank You"})
    response.delete_cookie("access_token")
    return response


###################################################### Shipment methods #################################################################

### Checks for user log in and session expiry and renders the create shipment page
@app.get("/shipment")
def shipment_get(request: Request):
    try:
        ### Checks if user is logged in and renders message if not logged in
        global loginUser
        if loginUser is None:
            return templates.TemplateResponse(LOGOUT_PAGE,{"request": request, "message":MSG_LOGIN}) 
        
        ### Calls decode_jwt to verify the session expiry time and renders message accordingly
        decoded_user =decode_jwt(request,loginUser)
        if(decoded_user is None):
            return templates.TemplateResponse(LOGOUT_PAGE,{"request": request,"message":MSG_SESSION_EXIPRED}) 
        
        ### Sets the minimum date for delivery date to be rendered in the page
        min_date = date.today()+ timedelta(days=1)

        ### Device id list for the device id drop down in the page
        device_id = ["1150","1151","1152","1153","1154","1155","1156","1157","1158"]

        return templates.TemplateResponse("/shipment.html",{"request": request, "deviceId": device_id,"expDel": min_date, "min_date": min_date}) 
    except Exception as error:
         raise HTTPException(status_code=404, detail= str(error))
    
         
### Checks for user log in and session expiry and calls function to create the shipment in db    
@app.post("/shipment")
async def shipment_post(request: Request):
    try:
        ### Checks if user is logged in and renders message if not logged in
        global loginUser
        if loginUser is None:
            return templates.TemplateResponse(LOGOUT_PAGE,{"request": request, "message":MSG_LOGIN}) 
        
        ### Calls decode_jwt to verify the session expiry time and renders message accordingly
        decoded_user =decode_jwt(request,loginUser)
        if(decoded_user is None):
            return templates.TemplateResponse(LOGOUT_PAGE,{"request": request,"message":MSG_SESSION_EXIPRED}) 
        
        ### Fetches the shipment details entered by user from the page and calls the shipment_create with the details
        shipment = await request.form()
        ship_num= await shipment_create(shipment,loginUser['id'])

        ### Renders the shipment created page with the shipment number
        return templates.TemplateResponse("/shpcreated.html",{"request": request,"shipNum": ship_num})
    except Exception as error:
         raise HTTPException(status_code=404, detail= str(error))
    
         
### Renders the the shipment created page   
@app.get("/shpcreated")
def shpcreated_get(request: Request):
    return templates.TemplateResponse("/shpcreated.html",{"request": request}) 


################################################ Datastream methods ###############################################################

### Checks for user log in and session expiry and renders the data stream page with the respective shipment details and device data 
@app.get("/datastream/{ship_num}")
def datastream_get(request: Request,ship_num:int):
    try:
        ### Checks if user is logged in and renders message if not logged in
        global loginUser
        if loginUser is None:
            return templates.TemplateResponse(LOGOUT_PAGE,{"request": request, "message":MSG_LOGIN}) 
        
        ### Calls decode_jwt to verify the session expiry time and renders message accordingly
        decoded_user =decode_jwt(request,loginUser)
        if(decoded_user is None):
            return templates.TemplateResponse(LOGOUT_PAGE,{"request": request,"message":MSG_SESSION_EXIPRED})
        
        ### Calls get_shipment_shipnum and get_device_data to get the shipment and device data respectively
        shipment = get_shipment_shipnum(ship_num)
        device_data =get_device_data(shipment[0]["device"])
       
        return templates.TemplateResponse("/datastream.html",{"request": request, "deviceData": device_data,"shipment":shipment[0]}) 
    
    except Exception as error:
         raise HTTPException(status_code=404, detail= str(error))
         
    
############################################### Dashboard/Home methods ##############################################################

### Checks for user log in and session expiry renders the dashboard/home page along with the user and shipment details
@app.get("/dashboard") 
def dashboard_get(request: Request):
    try:
        ### Checks if user is logged in and renders message if not logged in
        global loginUser
        if loginUser is None:
            return templates.TemplateResponse(LOGOUT_PAGE,{"request": request, "message":MSG_LOGIN}) 
        
        ### Calls decode_jwt to verify the session expiry time and renders message accordingly 
        decoded_user =decode_jwt(request,loginUser)
        if(decoded_user is None):
            return templates.TemplateResponse(LOGOUT_PAGE,{"request": request,"message":MSG_SESSION_EXIPRED}) 
        
        ### Fetches the shipments for the user
        shipments = get_shipment(loginUser) 
    
        return templates.TemplateResponse("/dashboard.html",{"request": request, "user": loginUser, "shipment": shipments})  
    except Exception as error:
         raise HTTPException(status_code=404, detail= str(error))
         
    
 ################################################### Forgot Password methods ######################################################

### Renders the forgot password page 
@app.get("/forgotPassword")
def forgot_pwd_get(request: Request):
   return templates.TemplateResponse("/forgotPassword.html",{"request": request}) 

    
### Validates the email entered and calls the function to send email with the new generated password    
@app.post("/forgotPassword")
def forgot_pwd_post(request: Request,email: str = Form(...)): 
    try: 
        ### Validates the email id for correctness
        errors =  email_valid(email)
        if errors is not None:
            return templates.TemplateResponse("/forgotPassword.html",{"request": request, "errors": [errors],"email": email})
        
        ### Calls generate_auth_email function to generate the password and send email and to set the generated password in db
        generate_auth_email(email)

        ### Renders the mail successfully sent page
        return templates.TemplateResponse(LOGOUT_PAGE,{"request": request,"message":"Password sent successfully to the email id.Please change the password after login"}) 
    
    except Exception as error:
         raise HTTPException(status_code=404, detail= str(error))
         

############################################ Change Password methods ###################################################################

### Checks for user log in and session expiry and renders the change password page for the user
@app.get("/changepassword")
def chg_pwd_get(request: Request):
    try:
        ### Checks if user is logged in and renders message if not logged in
        global loginUser
        if loginUser is None:
             return templates.TemplateResponse(LOGOUT_PAGE,{"request": request, "message":MSG_LOGIN}) 
        
        ### Calls decode_jwt to verify the session expiry time and renders message accordingly 
        decoded_user =decode_jwt(request,loginUser)
        if(decoded_user is None):
            return templates.TemplateResponse(LOGOUT_PAGE,{"request": request,"message":MSG_SESSION_EXIPRED}) 
        
        return templates.TemplateResponse(CHG_PWD_PAGE,{"request": request})  
    
    except Exception as error:
         raise HTTPException(status_code=404, detail= str(error))


### Checks for user log in and session expiry. Validates the passwords entered and calls the function to update the db with new password
@app.post("/changepassword")
def chg_pwd_post(request: Request,currentpwd: str = Form(...),newpwd:str = Form(...)):
    try:
        ### Checks if user is logged in and renders message if not logged in
        global loginUser
        if loginUser is None:
             return templates.TemplateResponse(LOGOUT_PAGE,{"request": request, "message":MSG_LOGIN}) 
        
        ### Calls decode_jwt to verify the session expiry time and renders message accordingly
        decoded_user =decode_jwt(request,loginUser)
        if(decoded_user is None):
            return templates.TemplateResponse(LOGOUT_PAGE,{"request": request,"message":MSG_SESSION_EXIPRED}) 
        
        ### Checks if current password is same as login user password and current and new password are not same
        if(currentpwd == loginUser['password']):
            if currentpwd != newpwd:
                ### Calls changepwd function to update the db with new password for the user
                changepwd( loginUser['email'],newpwd)
            else:
                return templates.TemplateResponse(CHG_PWD_PAGE,{"request": request, "error": "New Password cannot be same as current password","currentpwd": currentpwd, "newpwd":newpwd})
        else:
             return templates.TemplateResponse(CHG_PWD_PAGE,{"request": request, "error": "invalid current password","currentpwd": currentpwd, "newpwd":newpwd})

        ### Renders page with success message
        return templates.TemplateResponse(CHG_PWD_PAGE,{"request": request,"message": "Password changed Successfully"})  
    
    except Exception as error:
         raise HTTPException(status_code=404, detail= str(error))
         






  
