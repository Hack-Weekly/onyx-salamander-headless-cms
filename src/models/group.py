"""models/group.py

This file contains the Group models for the Onyx Salamander CMS database.
"""
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from models.base import Node
from models.user import User
from models.file import File
from models.comment import Comment

class Group(BaseModel):
    Admin: User
    Name: str
    Members: Optional[List[User]] = None