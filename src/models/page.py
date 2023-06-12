"""models/page.py

This file contains the Page models for the Onyx Salamander CMS database.
"""
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from models.base import Node
from models.comment import Comment

class URI(BaseModel):
    """URI represents a URL within the Onyx Salamander CMS

    URI's do NOT have UID, instead we query by URL which MUST be unique!
    """
    URL: str
    # LinkedFile: Optional[File] = None
    Description: Optional[str] = None
    # Access Control
    RequiresAuth: Optional[bool] = False
    # RequiresGroup: List[Optional[Group]] = None
    # User Metadata
    Modifier: Optional[str] = None
    Creator: Optional[str] = None
    # Datetime Metadata
    CreatedDate: Optional[datetime] = None
    ModifiedDate: Optional[datetime] = None
    ArchivedDate: Optional[datetime] = None

# Page Model
class Page(BaseModel):
    """Page represents a single web page within the Onyx Salamander CMS.
    """
    Title: str
    Headline: str
    Language: str
    PageType: str
    URL: Optional[str] = None
    Intro: Optional[str] = None
    Tagline: Optional[str] = None
    Description: Optional[str] = None
    # Comments: Optional[List[Comment]] = None

    # Metadata
    Keywords: Optional[List[str]] = None

    # User Metadata
    Modifier: Optional[str] = None # Who last modified page
    Creator: Optional[str] = None # Who created the page
    Owner:  Optional[str] = None # Who owns the page
    # Datetime Metadata
    CreatedDate: Optional[datetime] = None
    ModifiedDate: Optional[datetime] = None
    PublishDate: Optional[datetime] = None # Can be used to time page creation
    ReviewDate: Optional[datetime] = None
    ArchiveDate: Optional[datetime] = None
    

# Link Model
class Link(BaseModel):
    """Links represent hyperlinks in the Onyx Salamander CMS
    """
    Title: str
    URL: URI
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
