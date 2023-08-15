
from fastapi import HTTPException

from db_mongodb.db import user_collection

import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random,string

import os
from dotenv import load_dotenv

### Loads the env variables
load_dotenv()

### Generates Passcode and sends it as password to the email entered by the user in forgot password page. 
### Also calls function to update the generated password in DB
def generate_auth_email(receiver_mail: str):
    try:
        passcode = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
      
        subject = "scmxpertlite password"
        body ="\nHi,\n\n Your Password is "+str(passcode)
        
        sender_email=os.getenv('SENDER_EMAIL')
        receiver_email = receiver_mail
        password=os.getenv('SENDER_EMAIL_PASSWORD')

        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = ", ".join(receiver_email)
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))
        text = message.as_string()

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, text)

        ### Calls the changepwd function to update the generated password in DB for the mail id   
        changepwd(receiver_mail,passcode)

    except Exception as error:
         raise HTTPException(status_code=404, detail= str(error))
    
### Updates the password in DB for the given mail id     
def changepwd(email: str,password:str):
    user_collection.find_one_and_update( { 'email': email}, { '$set': { 'password': password} } ) 

    
