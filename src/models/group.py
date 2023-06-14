"""models/group.py

This file contains the Group models for the Onyx Salamander CMS database.
"""
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from models.user import User


class Group(BaseModel):
    Admin: User
    Name: str
    Description: Optional[str] = None
    Members: Optional[List[str]] = None
