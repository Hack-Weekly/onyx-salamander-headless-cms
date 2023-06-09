"""models/user.py

This file contains the models needed for User interaction
"""
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List
from onyx import settings

class User(BaseModel):
    """User class contains the structure of users within the graph database.
    """
    ScreenName: str
    Email: str
    HashedPassword: str
    UUID: Optional[str] = None
    Salt: Optional[str] = None  # Per user salt, randomly generated
    SaltPos: Optional[int] = None  # What position salt is inserted
    Phone: Optional[str] = None
    FirstName: Optional[str] = None
    MiddleName: Optional[str] = None
    LastName: Optional[str] = None
    LastSeen: Optional[datetime] = None
    Joined: Optional[datetime] = None
    Disabled: Optional[bool] = None
    Banned: Optional[bool] = None