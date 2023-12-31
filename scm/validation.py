
import re

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

### Validates the username,email and password entered in register page for correctness and returns list of error messages if any
def credential_valid(username:str,email:str,password:str) -> list:
        errors = []
        global regex
        if not username or len(username) <= 3:
           errors.append("Username should be > 3 chars")
        email_err = email_valid(email)
        if  email_err is not None:
             errors.append(email_err)
        if not password or len(password) < 5:
            errors.append("Password must be minimum 5 chars")
        return errors

### Validates the email entered in login page for correctness and returns error message if any
def email_valid(email: str)->str|None:
    global regex
    if not (re.fullmatch(regex, email)):
           return "Not a valid email"
    return None
