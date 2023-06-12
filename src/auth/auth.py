"""auth/auth.py

Onyx Salamander API Authentication Routes
"""
import uuid
from fastapi import APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, HTTPBasicCredentials, HTTPBasic
from typing import Optional, List
from onyx import settings
from auth.utils import *
from models.base import Token, TokenData
from models.user import User
from datetime import datetime

# API Router
router = APIRouter()

ROUTE = {
        "router":router,
        "prefix":settings.AUTH_ENDPOINT,
        "tags":["Authorization"]
} 

# Endpoint for registration
@router.post("/register")
async def RegisterUser(screenName: str, email: str, password: str,
                       phone: Optional[str] = None,
                       fname: Optional[str] = None,
                       mname: Optional[str] = None,
                       lname: Optional[str] = None):
    """Checks if a user exists and if not registers the new user, and
    returns the User instance.
    """
    # Check email validity
    if not ValidateEmail(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email {email} is not a valid email address.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    # Check password complexity
    if settings.FORCE_COMPLEX and not ValidatePasswordComplexity(password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password {password} must have a minimum of 8 characters, 1 upper case, 1 lower case, 1 number, and 1 special char.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    # Create a salt
    salt, saltPos = CreateSalt(len(password))
    salted = SaltPassword(password, salt, saltPos)
    # Hash the password
    phash = CreatePasswordHash(salted)
    # Create dictionary of new user attributes
    attributes = {
        "ScreenName": screenName,
        "Email": email,
        "HashedPassword": phash,
        "UUID":str(uuid.uuid4()),
        "Salt": salt,
        "SaltPos": saltPos,
        "Phone": phone,
        "FirstName": fname,
        "MiddleName": mname,
        "LastName": lname,
        "LastSeen": str(datetime.now(settings.SERVER_TIMEZONE)),
        "Joined": str(datetime.now(settings.SERVER_TIMEZONE)),
        "Disabled": False,
        "Banned": False,
    }
    cypher_create = 'CREATE (user:User $params) RETURN user'

    with settings.DB_DRIVER.session() as session:
        # Check if user exists
        if GetUser(email):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Operation not permitted, user with email: {email} already exists.",
                headers={"WWW-Authenticate": "Bearer"}
            )
        # Otherwise, create a new user
        response = session.run(query=cypher_create, parameters={
            'params': attributes
        })
        user_data = response.data()[0]['user']

    return User(**user_data)


@router.post("/login", response_model=User)
async def LoginHTTPBasic(credentials: HTTPBasicCredentials = Depends(HTTPBasic())):
    if not settings.ENABLE_HTTP_AUTH:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="HTTP Basic Authentication Has Been Disabled.")
    user = AuthenticateUser(credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"}
        )
    return user

@router.post("/token", response_model=Token)
async def LoginAccessToken(form_data: OAuth2PasswordRequestForm = Depends(), expires: Optional[timedelta] = None):
    if not settings.ENABLE_BEARER_AUTH:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Token Authentication Has Been Disabled")

    user = AuthenticateUser(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    if expires:
        token = CreateAccessToken(
            data={"email": user.Email}, expires_delta=expires)
    else:
        token = CreateAccessToken(data={"email": user.Email})
    return {"access_token": token, "token_type": "bearer"}
