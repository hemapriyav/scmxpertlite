
# from db_mongodb.model import User
# import db_mongodb.model as model


import re
regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
def credential_valid(username:str,email:str,password:str) -> list:
        errors = []
        global regex
        if not username or not len(username) > 3:
           errors.append("Username should be > 3 chars")
        if not (re.fullmatch(regex, email)):
            errors.append("Not a valid email")
        if not password or not len(password) >= 5:
            errors.append("Password must be > 4 chars")
        # if not errors:
        #     return errors
        return errors
def email_valid(email: str)->str:
    global regex
    if not (re.fullmatch(regex, email)):
           return "Not a valid email"
    return None