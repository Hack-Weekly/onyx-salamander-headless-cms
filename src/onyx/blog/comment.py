"""onyx/blog/comment.py

This file contains the CRUD operations for comments in the
Onyx Salamander CMS database
"""
import uuid
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile

# Import utils for database access & models
from onyx import settings
from auth.auth import GetCurrentActiveUser
from models.user import User
from models.comment import Comment
from models.file import File
from onyx.blog.file import CreateFile, DeleteFile

# Setup API Router
router = APIRouter()

ROUTE = {
    "router": router,
    "prefix": "/comment",
    "tags": ["Comment"]
}


def GetComment(UUID: str, GetAttached=False):
    basic = f"""MATCH (comment:Comment) WHERE comment.UUID = "{UUID}" RETURN comment"""

    if GetAttached:
        cypher_search = """MATCH (comment:Comment {UUID: $uid})-[r:ATTACHES]->(f:File)
        RETURN f, comment
        """
        files = []
        comment = None
        with settings.DB_DRIVER.session() as session:
            res = session.run(query=cypher_search,
                              parameters={"uid": UUID}).data()
        if res:
            comment = Comment(**res[0]["comment"])
            for each in res:
                if each["f"]:
                    files.append(File(**each["f"]))
        else:
            with settings.DB_DRIVER.session() as session:
                res = session.run(query=basic).data()
                if res:
                    comment = Comment(**res[0]["comment"])

        return {"Comment": comment, "Attachments": files}

    else:
        with settings.DB_DRIVER.session() as session:
            res = session.run(query=basic).data()
            if res:
                return Comment(**res[0]["comment"])

# Create a comment


@router.post("/create", response_model=Comment)
async def CreateComment(message: str,
                        commentOn: str,
                        linkedFiles: Optional[List[UploadFile]] = None,
                        published: Optional[bool] = True,
                        user: User = Depends(GetCurrentActiveUser)):
    UUID = str(uuid.uuid4())
    date = str(datetime.now(settings.SERVER_TIMEZONE))
    attributes = {
        "UUID": UUID,
        "Message": message,
        "Published": published,
        "Likes": 0,
        "Dislikes": 0,
        "Creator": user.UUID,
        "CreatedDate": date,
        "ModifiedDate": date,
    }
    cypher_matches = f"""MATCH (user:User) WHERE user.UUID = "{user.UUID}"
    MATCH (commentOn) WHERE commentOn.UUID = "{commentOn}"
    """
    cypher_creates = """
    CREATE (comment:Comment $params)
    CREATE (user)-[madeComment:OWNS]->(comment)
    CREATE (comment)-[isOn:ON]->(commentOn)
    """
    files = []
    if linkedFiles:
        # Upload each file and attach to comment
        i = 0
        for file in linkedFiles:
            f = await CreateFile(file, user=user)
            if f:
                cypher_matches += f"""
                MATCH (file{i}:File)
                WHERE file{i}.UUID = "{f.UUID}"
                """
                cypher_creates += f"""
                CREATE (comment)-[linksTofile{i}:ATTACHES]->(file{i})
                """
                i += 1
    cypher = cypher_matches + cypher_creates + " RETURN comment "
    with settings.DB_DRIVER.session() as session:
        res = session.run(query=cypher, parameters={
                          "params": attributes}).data()

    return Comment(**res[0]["comment"])

# List Comments


@router.get("/list/{UUID}", response_model=List[Comment])
async def ListComments(UUID: str):
    """Returns all comments attached to an item
    """
    cypher = """MATCH (comment:Comment)-[r:ON]->(n {UUID: $uid})
    RETURN comment
    """
    comments = []
    with settings.DB_DRIVER.session() as session:
        res = session.run(query=cypher, parameters={"uid": UUID}).data()
        for each in res:
            comments.append(Comment(**each["comment"]))

    return comments

# Read a comment


@router.get("/read/{UUID}")
async def ReadComment(UUID: str, GetAttached: bool = True):
    return GetComment(UUID=UUID, GetAttached=GetAttached)

# Update Comment


@router.put("/update/{UUID}", response_model=Comment)
async def UpdateComment(UUID: str, message: Optional[str] = None,
                        deleteFiles: Optional[List[str]] = None,
                        linkedFiles: Optional[List[UploadFile]] = None,
                        published: Optional[bool] = True,
                        user: User = Depends(GetCurrentActiveUser)):
    date = str(datetime.now(settings.SERVER_TIMEZONE))
    attributes = {
        "Message": message,
        "Published": published,
        "ModifiedDate": date,
    }
    c = GetComment(UUID=UUID, GetAttached=True)
    comment = c["Comment"]
    files = c["Attachments"]
    if not user.Admin and not comment.Creator:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You cannot edit that comment."
        )
    # Handle file deletion
    if deleteFiles and files:
        for file in files:
            if file.UUID in deleteFiles:
                await DeleteFile(UUID=file.UUID, user=user)
            elif file.Filename in deleteFiles:
                await DeleteFile(UUID=file.UUID, user=user)

    cypher_matches = f"""MATCH (comment:Comment)
    WHERE comment.UUID = "{UUID}"
    """
    cypher_creates = ""

    # Handle file uploading
    if linkedFiles:
        # Upload each file and attach to comment
        i = 0
        for file in linkedFiles:
            f = await CreateFile(file, user=user)
            if f:
                cypher_matches += f"""
                MATCH (file{i}:File)
                WHERE file{i}.UUID = "{f.UUID}"
                """
                cypher_creates += f"""
                CREATE (comment)-[linksTofile{i}:ATTACHES]->(file{i})
                """
                i += 1
    cypher = cypher_matches
    cypher += cypher_creates
    cypher += """ SET comment += $attributes
    RETURN comment
    """

    with settings.DB_DRIVER.session() as session:
        res = session.run(query=cypher, parameters={
                          "attributes": attributes}).data()
    return Comment(**res[0]["comment"])

# Delete Comment


@router.post("/delete/{UUID}")
async def DeleteComment(UUID: str,
                        deleteLinked: bool = True,
                        user: User = Depends(GetCurrentActiveUser)):
    """DeleteComment()

    UUID:str - Comment UUID
    deleteLinked - Whether to delete linked files
    """
    comment, files = GetComment(UUID=UUID, GetAttached=True)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found."
        )
    if not user.Admin and comment.Creator != user.UUID:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You cannot delete this comment."
        )
    if deleteLinked and files != None:
        for file in files:
            await DeleteFile(UUID=file.UUID, user=user)
    cypher = f"""MATCH (comment:Comment)
    WHERE comment.UUID = {UUID}
    DETACH DELETE comment
    """
    with settings.DB_DRIVER.session() as session:
        result = session.run(query=cypher)
        rel = result.data()
    # rel should be empty, if not this _should_ return an error message
    return rel or {
        "response": f"Comment was successfully deleted."
    }
