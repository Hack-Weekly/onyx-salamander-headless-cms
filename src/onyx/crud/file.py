"""onyx/crud/file.py

This file handles CRUD functionality for files in the Onyx Salamander CMS
"""
import uuid
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
# Import utilities for database access & File model

from onyx import settings
from auth.auth import GetCurrentActiveUser, GetCurrentActiveUserAllowGuest
from models.base import Relationship
from models.user import User
from models.group import Group
from models.file import File
from models.comment import Comment
from models.page import Page, URI, Link

# Setup API Router
router = APIRouter()

ROUTE = {
    "router":router,
    "prefix":"/crud",
    "tags":["File"]
}

def GetFile(fname: str):
    pass

# Create
@router.post("/create/file",response_model=File)
async def CreateFile():
    pass

# Read
@router.post("/read/file",response_model=File)
async def CreateFile():
    pass

# List
@router.post("/list/file",response_model=File)
async def CreateFile():
    pass

# Update
@router.post("/update/file",response_model=File)
async def CreateFile():
    pass

# Delete
@router.post("/delete/file",response_model=File)
async def CreateFile():
    pass
