"""models/file.py

This file contains the File models for the Onyx Salamander CMS database.
"""
from typing import Optional, Any
from pydantic import BaseModel
from fastapi.responses import FileResponse
from datetime import datetime
from models.user import User

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


class GraphFileResponse(FileResponse):

    def __init__(self, file:File, kwargs):
        super().__init__(**kwargs)
        self.fileObject = file
        
    def render(self, content: Any) -> bytes:
        return super().render(content), self.fileObject