"""models/blog-post.py

This represents a blog post within the Onyx Salamander CMS.
"""

from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


class BlogPost(BaseModel):
    UUID: str
    Title: str
    # Author: str
    Content: str
    Published: Optional[bool] = False
    Tags: Optional[List[str]] = None
    # FeaturedImage: Optional[Image] = None
    # Comments: Optional[List[Comment]] = None

    # Metadata
    Keywords: Optional[List[str]] = None

    # User Metadata
    Modifier: Optional[str] = None  # Who last modified the blog post
    Creator: Optional[str] = None  # Who created the blog post
    Owner: Optional[str] = None  # Who owns the blog post

    # Datetime Metadata
    CreatedDate: Optional[datetime] = None
    ModifiedDate: Optional[datetime] = None
    PublishedDate: Optional[datetime] = None
    ReviewDate: Optional[datetime] = None
    ArchiveDate: Optional[datetime] = None
