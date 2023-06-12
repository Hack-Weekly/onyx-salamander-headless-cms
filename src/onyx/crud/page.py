"""onyx/crud/crud_page.py

This file handles CRUD functionality for Pages in the Onyx Salamander CMS
"""
import uuid
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status

# Import utilities for database access & Page model
from onyx import settings
from auth.auth import GetCurrentActiveUser, GetCurrentActiveUserAllowGuest
from models.base import Relationship
from models.user import User
from models.file import File
from models.comment import Comment
from models.page import Page, URI, Link

from onyx.crud.url import _CreateURL

# Setup API Router
router = APIRouter()
# Create a second one so we can also link pages to root /
page_router = APIRouter() 
ROUTE = {
        "router":router,
        "prefix":"/crud",
        "tags":["Page"]
}

def GetPage(url:Optional[str]=None, title:Optional[str]=None):
    if url:
        cypher_search = f"MATCH (page:Page) WHERE page.URL = '{url}' RETURN page"
    elif title:
        cypher_search = f"MATCH (page:Page) WHERE page.Title = '{title}' RETURN page"

    with settings.DB_DRIVER.session() as session:
        result = session.run(query=cypher_search).data()
        if result:
            return Page(**result[0]["page"])
    return False

@router.post("/create/page", response_model=Page)
async def CreatePage(title: str, headline:str, language:str,
                     pageType:str, url:str, intro:Optional[str]=None,
                     tagline:Optional[str]=None,
                     description:Optional[str]=None,
                     keywords:Optional[List[str]] = None,
                     publishDate: Optional[datetime] = None,
                     reviewDate: Optional[datetime] = None,
                     archiveDate: Optional[datetime] = None,
                     user: User = Depends(GetCurrentActiveUser)
                     ):
    """CreatePage - Creates a new page"""
    # Check that Page does not exist
    if GetPage(title=title):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Operation not permitted. Page with Title: {title} already exists.",
            headers={"WWW-Authenticate":"Bearer"}
        )
    date = str(datetime.now(settings.SERVER_TIMEZONE))

    attributes = {
        "Title":title,
        "Headline":headline,
        "Language":language,
        "PageType":pageType,
        "URL":url,
        "Creator":user.UUID,
        "Modifier":user.UUID,
        "Owner":user.UUID,
        "CreatedDate": date,
        "ModifiedDate": date,
        "PublishDate": date,
    }
    if publishDate:
        attributes["PublishDate"]=publishDate
    if intro: attributes["Intro"]=intro
    if tagline: attributes["Tagline"]=tagline
    if description: attributes["Description"]=description
    if keywords: attributes["Keywords"]=keywords
    if reviewDate: attributes["ReviewDate"]=reviewDate
    if archiveDate: attributes["ArchiveDate"]=archiveDate

    _CreateURL(url=url, user=user, description=description)

    cypher = f"""MATCH (user:User) WHERE user.UUID = "{user.UUID}"
    MATCH (url:URL) WHERE url.URL = "{url}"
    CREATE (page:Page $params)
    CREATE (user)-[relationship:OWNS]->(page)
    CREATE (url)-[relationship2:LINKS]->(page)
    RETURN page
    """
    with settings.DB_DRIVER.session() as session:
        res = session.run(query=cypher, parameters={"params":attributes})
        page = res.data()[0]
        print("PAGE:",page)
        page=page["page"]

    return Page(**page)

# Read Pages
@page_router.get("/{url}", response_model=Page)
@router.post("/read/page/{url}", response_model=Page)
async def ReadPage(url: str):
    p = GetPage(url=url)
    if not p:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Nothing found for /{url}"
        )
    return p
# List Pages
@router.get("/list/pages", response_model=List[Page])
async def ListPages(limit:int=25):
    cypher = f"MATCH (page:Page) return page LIMIT {limit}"
    out = []
    with settings.DB_DRIVER.session() as session:
        result = session.run(query=cypher)
        rel = result.data()
        for page in rel:
            out.append(Page(**page["page"]))
    return out

# Update Pages
@router.post("/update/page/{url}", response_model=Page)
async def UpdatePage(url:str, user:User = Depends(GetCurrentActiveUser)):
    pass

# Delete Pages
@router.post("/delete/page/{url}")
async def DeletePage(url:str, user:User = Depends(GetCurrentActiveUser)):
    page = GetPage(url=url)
    if page and not page.Owner == user.UUID:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"You do not have write access to {url}.",
            headers={"WWW-Authenticate":"Bearer"}
        )
    cypher = f"""MATCH (page:Page) WHERE page.URL = "{url}"
    DETACH DELETE page"""
    with settings.DB_DRIVER.session() as session:
        result = session.run(query=cypher)
        rel = result.data()
    # rel should be empty, if not this _should_ return an error message
    return rel or {
        "response":f"Page {url} was successfully deleted."
    }