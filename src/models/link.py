"""models/link.py

This file contains the Link models for the Onyx Salamander CMS database.
"""
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

# Link Model
class Link(BaseModel):
    """Links represent hyperlinks in the Onyx Salamander CMS
    """
    Title: str
    LinkType: Optional[str] = None
    Flyover: Optional[str] = None
    # Metadata
    Keywords: Optional[str] = None
    # User Metadata
    Creator: Optional[str] = None # Who created the page
    Modifier: Optional[str] = None # Who last modified page
    # Datetime Metadata
    CreatedDate: Optional[datetime] = None
    ModifiedDate: Optional[datetime] = None
    PublishDate: Optional[datetime] = None # Can be used to time page creation
    ArchiveDate: Optional[datetime] = None
