"""onyx/blog/file.py

This file handles CRUD functionality for files in the Onyx Salamander CMS
"""
import uuid
from tempfile import SpooledTemporaryFile
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import UploadFile
# Import utilities for database access & File model

from onyx import settings
from auth.auth import GetCurrentActiveUser, GetCurrentActiveUserAllowGuest
from models.user import User
from models.file import File as DBFile

# Setup API Router
router = APIRouter()

ROUTE = {
    "router": router,
    "prefix": "/file",
    "tags": ["File"]
}


def GetFileHash(file: SpooledTemporaryFile, block_size: int = 2**20):
    hash = settings.HASH_FUNC()
    while True:
        data = file.read(block_size)
        if not data:
            break
        hash.update(data)
    return hash.hexdigest()


def GetFileFromDB(UUID: str):
    cypher = f"""MATCH (file:File)
    WHERE file.UUID = "{UUID}" 
    RETURN file
    """
    with settings.DB_DRIVER.session() as session:
        res = session.run(query=cypher).data()
        if not res:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"File: {UUID} not found.")
        res = res[0]
    f = DBFile(**res["file"])
    return f


def ReadFileFromStorage(dbFile: DBFile):
    if dbFile:
        return settings.STORAGE_DRIVER.ReadFile(dbFile.UUID, dbFile.Filename)

# Create


@router.post("/create", response_model=DBFile)
async def create_file(file: UploadFile, description: Optional[str] = None, user: User = Depends(GetCurrentActiveUser)):
    date = str(datetime.now(settings.SERVER_TIMEZONE))
    uid = str(uuid.uuid4())
    attributes = {
        "UUID": uid,
        "Filename": file.filename,
        "Type": file.content_type,
        "SizeBytes": file.size,
        "Creator": user.UUID,
        "Modifier": user.UUID,
        "CreatedDate": date,
        "ModifiedDate": date,
    }
    if settings.HASH_FILES:
        attributes["Hash"] = await GetFileHash(file)
    if description:
        attributes["Description"] = description

    # Upload file to storage
    await settings.STORAGE_DRIVER.WriteFile(uid, file)

    cypher = f"""MATCH (user:User) WHERE user.UUID = "{user.UUID}"
    CREATE (file:File $params)
    CREATE (user)-[relationship:OWNS]->(file)
    RETURN file
    """
    with settings.DB_DRIVER.session() as session:
        res = session.run(query=cypher, parameters={"params": attributes})
        f = res.data()[0]["file"]
    return DBFile(**f)

# Read


@router.get("/read/")
async def read_file(download: bool = True,
                   UUID: Optional[str] = None,
                   filename: Optional[str] = None,
                   user: User = Depends(GetCurrentActiveUserAllowGuest)):
    cypher = """MATCH (file:File)
    """
    if UUID:
        cypher += f"""WHERE file.UUID = "{UUID}" """
    elif filename:
        cypher += f"""WHERE file.Filename = "{filename}" """
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="No UUID or filename provided.")

    cypher += "RETURN file"

    with settings.DB_DRIVER.session() as session:
        res = session.run(query=cypher).data()
        if not res:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"File: {UUID} not found.")
        res = res[0]
    f = DBFile(**res["file"])
    file = ReadFileFromStorage(f)
    if download:
        return file
    return f

# List


@router.post("/list", response_model=List[DBFile])
async def list_file(limit: int = 25,
                   user: User = Depends(GetCurrentActiveUserAllowGuest)):
    cypher = f"""MATCH (file:File) RETURN file LIMIT {limit}"""
    files = []
    with settings.DB_DRIVER.session() as session:
        res = session.run(query=cypher).data()
        for file in res:
            files.append(DBFile(**file["file"]))
    return files


@router.post("/delete/{UUID}")
async def delete_file(UUID: str,
                     user: User = Depends(GetCurrentActiveUser)):
    cypher = f"""MATCH (file:File)
    WHERE file.UUID = "{UUID}"
    DETACH DELETE file
    """
    f = GetFileFromDB(UUID=UUID)
    if not f:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found.")
    if not user.Admin and f.Creator != user.UUID:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You are not allowed to delete this file.")
    settings.STORAGE_DRIVER.DeleteFile(f.UUID)
    with settings.DB_DRIVER.session() as session:
        res = session.run(query=cypher).data()
    return res or {
        "response": f"File {f.Filename} was successfully deleted."
    }
