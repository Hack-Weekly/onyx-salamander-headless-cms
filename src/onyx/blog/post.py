"""onyx/blog/post.py

This file handles blog post functionality for files in the Onyx Salamander CMS
"""
import uuid
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
# Import utilities for database access & File model

from onyx import settings
from models.blog_post import BlogPost
from auth.auth import GetCurrentActiveUser, GetCurrentActiveUserAllowGuest
from models.base import Relationship
from models.user import User
from models.group import Group
from models.comment import Comment
from models.page import Page, URI, Link

# Setup API Router
router = APIRouter()

ROUTE = {
    "router":router,
    "prefix":"/blog",
    "tags":["Blog"]
}

def GetBlogPost(UUID:Optional[str]=None,title:Optional[str]=None,user:Optional[User]=None):
    if UUID:
        cypher_search = f"MATCH (post:BlogPost) WHERE post.UUID = '{UUID}' "
    elif title:
        cypher_search = f"MATCH (post:BlogPost) WHERE post.Title = '{title}'"
    
    if not user:
        cypher_search += "AND post.Published = True"
    elif not user.Admin:
        cypher_search += f"AND post.Owner = '{user.UUID}'"

    cypher_search += " RETURN post"

    print("CY",cypher_search)

    with settings.DB_DRIVER.session() as session:
        result = session.run(query=cypher_search).data()
        if result:
            print(result)
            return BlogPost(**result[0]["post"])

# Create
@router.post("/create",response_model=BlogPost)
async def CreateBlogPost(title:str, content:str,
                        published: Optional[bool]=False,
                        tags: Optional[List[str]]=None,
                        keywords: Optional[List[str]]=None,
                        user: User = Depends(GetCurrentActiveUser)):
    date = str(datetime.now(settings.SERVER_TIMEZONE))
    attributes = {
        "UUID":str(uuid.uuid4()),
        "Title":title,
        "Content":content,
        "Creator":user.UUID,
        "Modifier":user.UUID,
        "Owner":user.UUID,
        "CreatedDate":date,
        "ModifiedDate":date
    }
    if published:
        attributes["Published"]=published
        attributes["PublishedDate"]=date
    if tags:
        attributes["Tags"]=tags
    if keywords:
        attributes["Keywords"]=keywords
    
    cypher = f"""MATCH (user:User) WHERE user.UUID = "{user.UUID}"
    CREATE (post:BlogPost $params)
    CREATE (user)-[relationship:OWNS]->(post)
    CREATE (user)-[relationship2:AUTHOR]->(post)
    RETURN post
    """

    with settings.DB_DRIVER.session() as session:
        res = session.run(query=cypher, parameters={"params":attributes})
        post = BlogPost(**res.data()[0]["post"])
    return post

# Read
@router.post("/read",response_model=Optional[BlogPost])
async def ReadBlogPost(UUID:Optional[str]=None,title:Optional[str]=None, user:User=Depends(GetCurrentActiveUserAllowGuest)):
    return GetBlogPost(UUID=UUID,title=title,user=user)

# List
@router.get("/list",response_model=List[BlogPost])
async def ListBlogPosts(limit:int=25, order_by:Optional[str]=None, user:User=Depends(GetCurrentActiveUserAllowGuest)):
    if not user:
        cypher = f"MATCH (post:BlogPost) WHERE post.Published = True RETURN post LIMIT {limit}"
    elif not user.Admin:
        cypher = f"""MATCH (post:BlogPost) WHERE post.Published = True
        OR post.Owner = "{user.UUID}"
        OR post.Creator = "{user.UUID}"
        RETURN post
        LIMIT {limit}
        """
    elif user.Admin==True:
        cypher = "MATCH (post:BlogPost) RETURN post LIMIT {limit}"

    if order_by:
        cypher += f" ORDER BY post.{order_by}"
    posts = []
    with settings.DB_DRIVER.session() as session:
        res = session.run(query=cypher).data()
        for each in res:
            post = BlogPost(**each["post"])
            posts.append(post)
    return posts

# Update
@router.post("/update",response_model=BlogPost)
async def UpdateBlogPost(UUID:str, attributes:dict, user:User = Depends(GetCurrentActiveUser)):
    date = str(datetime.now(settings.SERVER_TIMEZONE))
    post = GetBlogPost(UUID=UUID, user=user)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"You do not have write read/write access to the post or it does not exist."
        )
    cypher = f"""MATCH (post:BlogPost)
    WHERE post.UUID = "{UUID}"
    SET post += $attributes
    SET post.Modifier = "{user.UUID}"
    SET post.ModifiedDate = "{date}"
    """
    if "Published" in attributes.keys():
        if attributes["Published"]:
            cypher += f"""SET post.Published = True
            SET post.PublishedDate = "{date}"
            """
        else:
            cypher += f"""SET post.Published = False"""
        del attributes["Published"]
    cypher += "RETURN post"
    for key in attributes.keys():
        if key in settings.BASE_PROPERTIES:
            del attributes[key]
    with settings.DB_DRIVER.session() as session:
        res = session.run(query=cypher,parameters={"attributes":attributes})
        updated = BlogPost(**res.data()[0]["post"])
    return updated

# Delete
@router.post("/delete")
async def DeleteBlogPost(UUID:str, user:User = Depends(GetCurrentActiveUser)):
    post = GetBlogPost(UUID=UUID,user=user)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"You do not have write read/write access to the post, or it does not exist."
        )
    cypher = f"""MATCH (post:BlogPost)
    WHERE post.UUID = "{UUID}"
    DETACH DELETE post
    """

    with settings.DB_DRIVER.session() as session:
        res = session.run(query=cypher).data()
    return res or {
        "response":f"Blog post {UUID} was successfully deleted."
    }