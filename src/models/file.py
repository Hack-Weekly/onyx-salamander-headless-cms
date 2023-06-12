"""models/file.py

This file contains the File models for the Onyx Salamander CMS database.
"""
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from models.base import Node
from models.user import User

class File(Node):
    """File represents any file stored within the Onyx CMS database.
    """
    UUID: str
    Title: str
    Description: str
#    Comments: Optional[List[Comment]] = None

    # User Metadata
    Creator: Optional[User] = None
    Modifier: Optional[User] = None

    # Datetime Metadata
    CreatedDate: Optional[datetime] = None
    ModifiedDate: Optional[datetime] = None

