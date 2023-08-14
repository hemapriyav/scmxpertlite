

from fastapi import HTTPException
from db_mongodb.db import collection_name

import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import random,string

import os
from dotenv import load_dotenv
load_dotenv()

def generate_auth_email(receiver_mail: str):
    try:
        passcode = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        print("password-"+passcode)
        
        print("inside generate auth email")
        subject = "scmxpertlite password"
        body ="\nHi,\n\n Your Password is "+str(passcode)
        # sender_email="scmxpert1@gmail.com"
        sender_email=os.getenv('SENDER_EMAIL')
        receiver_email = receiver_mail
        # password="mlyjkttmugfhcigo"
        password=os.getenv('SENDER_EMAIL_PASSWORD')

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
        changepwd(receiver_mail,passcode)
    except Exception as error:
         raise HTTPException(status_code=404, detail= str(error))
    
def changepwd(email: str,password:str):
    collection_name.find_one_and_update( { 'email': email}, { '$set': { 'password': password} } ) 

    
