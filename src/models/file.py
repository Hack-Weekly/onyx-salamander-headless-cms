"""models/file.py

This file contains the File models for the Onyx Salamander CMS database.
"""
from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class File(BaseModel):
    """File represents any file stored within the Onyx CMS database.
    """
    UUID: str
    Filename: str
    Type: str
    SizeBytes: int
    Hash: Optional[str] = None
    Description: Optional[str] = None

    # User Metadata
    Creator: Optional[str] = None
    Modifier: Optional[str] = None

    # Datetime Metadata
    CreatedDate: Optional[datetime] = None
    ModifiedDate: Optional[datetime] = None
