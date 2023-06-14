"""models/comment.py

This file contains the Comment & related models for the Onyx Salamander
CMS database.
"""
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class Comment(BaseModel):
    UUID: str
    Message: str
    # LinkedFiles: Optional[List[str]] = None
    Published: Optional[bool] = None
    
    # Metadata
    Creator: Optional[str] = None
    Likes: Optional[int] = None
    Dislikes: Optional[int] = None
    # LikedBy: List[Optional[str]] = None
    # DislikedBy: List[Optional[str]] = None

    # Datetime Metadata
    CreatedDate: Optional[datetime] = None
    ModifiedDate: Optional[datetime] = None