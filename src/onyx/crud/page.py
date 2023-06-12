"""onyx/crud/crud_page.py

This file handles CRUD functionality for Pages in the Onyx Salamander CMS
"""
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status

# Import utilities for database access & Page model
from onyx import settings
from auth.auth import GetCurrentActiveUser
from models.user import User
from models.page import Page

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

def UpdatePageURL(original:str, new:str, user:User, delete_old:bool = True):
    # Create new URL
    _CreateURL(url=new, user=user)
    # Detach & Delete url
    cypher_detach = f"MATCH (url:URL) WHERE url.URL = '{original}'"
    if delete_old:
        cypher_detach += " DETACH DELETE url"
    else:
        cypher_detach += " DETACH url"
    # Update & attach page URL
    cypher = f"""
    MATCH (url:URL) WHERE url.URL = "{new}"
    MATCH (page:Page) WHERE page.URL = "{original}"
    SET page.URL = "{new}"
    CREATE (url)-[relationship:LINKS]->(page)
    RETURN page
    """
    with settings.DB_DRIVER.session() as session:
        session.run(query=cypher_detach).data()
        page = session.run(query=cypher).data()[0]["page"]
    return Page(**page)

@router.post("/create/page", response_model=Page)
async def CreatePage(title: str, headline:str, language:str,
                     pageType:str, url:Optional[str]=None, intro:Optional[str]=None,
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
        "Creator":user.UUID,
        "Modifier":user.UUID,
        "Owner":user.UUID,
        "CreatedDate": date,
        "ModifiedDate": date,
        "PublishDate": date,
    }
    if url:
        attributes["URL"]=url
    if publishDate:
        attributes["PublishDate"]=publishDate
    if intro:
        attributes["Intro"]=intro
    if tagline:
        attributes["Tagline"]=tagline
    if description:
        attributes["Description"]=description
    if keywords:
        attributes["Keywords"]=keywords
    if reviewDate:
        attributes["ReviewDate"]=reviewDate
    if archiveDate:
        attributes["ArchiveDate"]=archiveDate

    cypher = f"""MATCH (user:User) WHERE user.UUID = "{user.UUID}"
    CREATE (page:Page $params)
    CREATE (user)-[relationship:OWNS]->(page)
    """
    if url:
        _CreateURL(url=url, user=user, description=description)
        cypher += f"""MATCH (url:URL) WHERE url.URL = "{url}"
        CREATE (url)-[relationship2:LINKS]->(page)"""
        
    cypher += "RETURN page"
    
    with settings.DB_DRIVER.session() as session:
        res = session.run(query=cypher, parameters={"params":attributes})
        page = res.data()[0]
        page=page["page"]

    return Page(**page)

# Read Pages
@page_router.get("/{url}", response_model=Page)
@router.post("/read/page/", response_model=Page)
async def ReadPage(url: Optional[str]=None, title: Optional[str]=None):
    if url:
       p = GetPage(url=url)
    elif title:
        p = GetPage(title=title)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Must have page url or title."
        )
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
@router.put("/update/page/{url}", response_model=Page)
async def UpdatePage(url:str, attributes:dict, user:User = Depends(GetCurrentActiveUser)):
    time = str(datetime.now(settings.SERVER_TIMEZONE))
    page = GetPage(url=url)
    if page and not page.Owner == user.UUID:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"You do not have write access to {url}.",
            headers={"WWW-Authenticate":"Bearer"}
        )
    cypher = f"""MATCH (page:Page) WHERE page.URL = "{url}"
    SET page += $attributes
    SET page.Modifier = "{user.UUID}"
    SET page.ModifiedDate = "{time}"
    RETURN page
    """
    if "URL" in attributes.keys():
        UpdatePageURL(original=url, new=attributes["URL"], user=user)
        url = attributes["URL"]
        del attributes["URL"]
    for key in attributes.keys():
        if key in settings.BASE_PROPERTIES:
            del attributes[key]
    with settings.DB_DRIVER.session() as session:
        if not user.Admin:
            relate = session.run(query=f"""MATCH (user:User)-[relationship]->(page:Page)
            WHERE user.UUID = "{user.UUID}" AND page.URL = "{url}"
            RETURN relationship
            """).data()[0]
            if relate:
                if "OWNS" not in str(relate) and "CanModify" not in str(relate):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"You do not have write access to page {url}.",
                        headers={"WWW-Authenticate":"Bearer"}
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"You do not have write access to {url}.",
                    headers={"WWW-Authenticate":"Bearer"}
                )
        update = session.run(query=cypher, parameters={"attributes":attributes}).data()[0]
    return Page(**update["page"])
 
# Delete Pages
@router.post("/delete/page/{url}")
async def DeletePage(url:str, del_url:bool = True, user:User = Depends(GetCurrentActiveUser)):
    page = GetPage(url=url)
    if page and not page.Owner == user.UUID:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"You do not have write access to {url}.",
            headers={"WWW-Authenticate":"Bearer"}
        )
    cypher = f"""MATCH (page:Page) WHERE page.URL = "{url}"
    MATCH (url:URL) WHERE url.URL = "{url}"
    DETACH DELETE page
    """
    if del_url:
        cypher += "DETACH DELETE url"
    with settings.DB_DRIVER.session() as session:
        result = session.run(query=cypher)
        rel = result.data()
    # rel should be empty, if not this _should_ return an error message
    return rel or {
        "response":f"Page {url} was successfully deleted."
    }