"""models/comment.py

This file contains the Comment & related models for the Onyx Salamander
CMS database.
"""
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from models.base import Node
from models.user import User
from models.file import File

class Comment(Node):
    Message: str
    LinkedFiles: Optional[List[File]] = None
    Published: Optional[bool] = True
    
    # Metadata
    Creator: Optional[User] = None
    LikedBy: List[Optional[User]] = None
    DislikedBy: List[Optional[User]] = None

    # Datetime Metadata
    CreatedDate: Optional[datetime]
    ModifiedDate: Optional[datetime]