"""auth/utils.py

Onyx Salamander API Authentication Utilities

"""
import re
import secrets
import string
from jose import JWTError, jwt
from typing import Optional, List
from datetime import datetime, timedelta
from models.base import TokenData
from fastapi import Depends, HTTPException, status
from onyx import settings
from models.user import User, UserInDB

# RFC 5322 Regex Email Pattern
EMAIL_VALIDATE_PATTERN = "(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\\x01-\\x08\\x0b\\x0c\\x0e-\\x1f\\x21\\x23-\\x5b\\x5d-\\x7f]|\\\\[\\x01-\\x09\\x0b\\x0c\\x0e-\\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\\x01-\\x08\\x0b\\x0c\\x0e-\\x1f\\x21-\\x5a\\x53-\\x7f]|\\\\[\\x01-\\x09\\x0b\\x0c\\x0e-\\x7f])+)\\])"
# Password complexity
# Must have:
#   8 chars
#   1 Uppercase
#   1 Lowercase
#   1 Number
#   1 Special Char
PASSWORD_COMPLEXITY_PATTERN = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$"

def AuthenticateUser(email: str, pword: str):
    """AuthenticateUser - Authenticates a user and returns an instance of it.
        email: str
        pword: str

        Usage:
            user = AuthenticateUser('email@email.com', 'password')
            if user:
                # Authentication success!
    """
    user = GetUser(email)
    if user:
        return user if VerifyPassword(user, pword) else False
    return False

def CreatePasswordHash(pword: str):
    """CreatePasswordHash - Generates a hash of a password string.
        pword: str

        Usage:
            hash = CreatePasswordhash('password') 
    """
    return settings.PWD_CONTEXT.hash(pword)

def CreateSalt(plen: int):
    """CreateSalt - Creates a salt for a password size.
        plen: int - Password Length

        Usage:
            salt, saltPos = CreateSalt(len(password))
    """
    salt = ''.join(secrets.choice(string.ascii_uppercase
                                  + string.ascii_lowercase)
                   for i in range(settings.SALT_SIZE))
    saltPos = secrets.randbelow(plen)
    return salt, saltPos

def SaltPassword(pword:str, salt:str, saltPos:int):
    """SaltPassword - Salts a password and returns the resulting string
        pword: str
        salt: str
        saltPos: int

        Usage:
            salted = SaltPassword(password, salt, saltPos)
            # Or
            salted = SaltPassword(password, CreateSalt(len(password)))
    """
    if len(pword) < saltPos:
        # Wrong password, dump this goober
        return False
    return pword[:saltPos] + salt + pword[saltPos:]

def VerifyPassword(user:User, plain: str):
    """VerifyPassword - Verifies a plaintext password.
        user: User - use GetUser()
        plain: str - The plaintext password

        Usage:
            if(VerifyPassword(user, password)):
                # Authenticated successfully
    """
    salted = SaltPassword(plain, user.Salt, user.SaltPos)
    return settings.PWD_CONTEXT.verify(salted, user.HashedPassword)

def GetUser(email: str):
    """GetUser - Retrieves a user by email.
        email: email

        Usage:
            user = GetUser(email)
            if user:
                # User found!
    """
    cypher_search = f"MATCH (user:User) WHERE user.Email = '{email}' RETURN user"
    with settings.DB_DRIVER.session() as session:
        user = session.run(query=cypher_search)
        data = user.data()
        if len(data) > 0:
            user_data = data[0]['user']
            return UserInDB(**user_data)
    return None

def ValidateEmail(email: str):
    """ValidateEmail - Determines whether an email address is real or fake
        email: str

        Usage:
            if ValidateEmail(email):
                # Success!
    """
    if re.match(EMAIL_VALIDATE_PATTERN, email):
        return True
    return False

def ValidatePasswordComplexity(pword: str):
    """ValidatePasswordComplexity
        pword: str

        Usage:
            if ValidatePasswordComplexity(password):
                # password is complex
    """
    if re.match(PASSWORD_COMPLEXITY_PATTERN, pword):
        return True
    return False

# Token/OAuth stuff

def CreateAccessToken(data:dict, expires_delta: Optional[timedelta] = None):
    """CreateAccessToken - Creates an access token for OAuth2 flow
        data:dict
        expires_delta: Optional[timedelta] - Overrides server timeout

        Usage:
            access_token = CreateAccessToken(data={"user":user.email})
    """
    to_encode = data.copy()
    expire = datetime.now(settings.SERVER_TIMEZONE)
    if expires_delta:
        expire += expires_delta
    else:
        expire += timedelta(minutes=settings.TOKEN_LIFETIME_MINUTES)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

async def GetCurrentUser(token: str = Depends(settings.OAUTH2_SCHEME)):

    """GetCurrentUser - Used to decrypt auth tokens and return the user email
    """
    cred_except = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "Could not validate credentials.",
        headers = {"WWW-Authenticate", "Bearer"}
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        email: str = payload.get('email')
        if email is None:
            raise cred_except
        token_data = TokenData(Email=email)
    except JWTError as e:
        raise cred_except from e
    print("TOKEN: ", token_data.Email)
    user = GetUser(token_data.Email)
    if user is None:
        raise cred_except
    return user

async def GetCurrentActiveUser(current: User = Depends(GetCurrentUser)):
    """GetCurrentActiveUser - Used to ensure user account has not been disabled or banned
    """
    if current.Disabled:
        raise HTTPException(status_code=400, detail="User Inactive.")
    if current.Banned:
        raise HTTPException(status_code=400, detail="User Banned.")
    return current

def GetCurrentActiveUserAllowGuest(required: bool = False):
    """GetCurrentUserAllowGuest  
    """
    async def _get_user(current: User = Depends(GetCurrentActiveUser)):
        if not required and not current:
            return None
    return _get_user
