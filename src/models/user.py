"""models/user.py

This file contains the models needed for User interaction
"""
from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    """User class contains the structure of users within the graph database.
    """
    ScreenName: str
    Email: str
    UUID: Optional[str] = None
    Salt: Optional[str] = None  # Per user salt, randomly generated
    SaltPos: Optional[int] = None  # What position salt is inserted
    Phone: Optional[str] = None
    FirstName: Optional[str] = None
    MiddleName: Optional[str] = None
    # Metadata
    LastName: Optional[str] = None
    LastSeen: Optional[datetime] = None
    Joined: Optional[datetime] = None
    Disabled: Optional[bool] = False
    Banned: Optional[bool] = False
    Admin: Optional[bool] = False


class UserInDB(User):
    """UserInDB class, used to hide stuff like password hashes so we don't send that info back in a response.
    """
    HashedPassword: str
