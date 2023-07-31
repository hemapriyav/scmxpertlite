
import re

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

def credential_valid(username:str,email:str,password:str) -> list:
        errors = []
        global regex
        if not username or len(username) <= 3:
           errors.append("Username should be > 3 chars")
        if not (re.fullmatch(regex, email)):
            errors.append("Not a valid email")
        if not password or len(password) < 5:
            errors.append("Password must be minimum 5 chars")
        return errors

def email_valid(email: str)->str|None:
    global regex
    if not (re.fullmatch(regex, email)):
           return "Not a valid email"
    return None
