"""onyx/crud/crud_url.py

This file handles CRUD functionality for URL's and Links in the Onyx Salamander CMS
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
from models.group import Group
from models.file import File
from models.comment import Comment
from models.page import Page, URI, Link

# Setup API Router
router = APIRouter()

ROUTE = {
        "router":router,
        "prefix":"/crud",
        "tags":["URL"]
} 

def GetURL(url:str, contains:Optional[bool]=False):
    if contains:
        cypher_search = f"MATCH (url:URL) WHERE url.URL CONTAINS '{url}' RETURN url"
    else:
        cypher_search = f"MATCH (url:URL) WHERE url.URL = '{url}' RETURN url"
    with settings.DB_DRIVER.session() as session:
        result = session.run(query=cypher_search).data()
        if result:
            return URI(**result[0]['url'])
    return False

def _CreateURL(url: str,
                    user: User,
                    description: Optional[str] = None,
                    requireAuth: Optional[bool] = False,
                    requiresGroup: Optional[List[str]] = None,
                    linkedFile: Optional[File] = None,
                    ):
    # Check that URL does not exist
    if GetURL(url=url):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Operation not permitted. URL `{url}` already exists.",
            headers={"WWW-Authenticate":"Bearer"}
        )
    attributes = {
        "URL":url,
        "Description":description,
        "RequiresAuth":requireAuth,
        "Modifier":user.UUID,
        "Creator":user.UUID,
        "CreatedDate":str(datetime.now(settings.SERVER_TIMEZONE)),
        "ModifiedDate":str(datetime.now(settings.SERVER_TIMEZONE)),
    }
    cypher = f"""MATCH (user:User) WHERE user.UUID="{user.UUID}"
    CREATE (url:URL $params)
    CREATE (user)-[relationship1:OWNS]->(url) 
    """
    if linkedFile:
        cypher += f"""MATCH (file:File) WHERE file.UUID="{File.UUID}"
        CREATE (url)-[relationship2:LINKS]->(file)
        """
    cypher += """RETURN url"""
    with settings.DB_DRIVER.session() as session:
        res = session.run(query=cypher, parameters={"params":attributes})
        url_data = res.data()[0]["url"]
    
    if requiresGroup:
        i=3
        for group in requiresGroup:
            cypher += f"""MATCH (group:Group) WHERE group.Name="{group}"
            MATCH (url:URL) WHERE url.URL = "{url}"
            CREATE (url)-[relationship{i}:REQUIRES]->(group)
            RETURN url
            """
            i+=1
            with settings.DB_DRIVER.session() as session:
                url_data = res.data()[0]["url"]
    return URI(**url_data)

@router.post("/create/url", response_model=URI)
async def CreateURL(url: str,
                    description: Optional[str] = None,
                    requireAuth: Optional[bool] = False,
                    requireGroup: Optional[List[str]] = None,
                    user: User = Depends(GetCurrentActiveUser)
                    ):
    """CreateURL - Creates a new URL"""
    return _CreateURL(url=url, description=description,
                      requireAuth=requireAuth, requiresGroup=requireGroup,
                      user=user)

@router.post("/read/url/{url}", response_model=URI)
async def ReadURL(url: str, user: User = Depends(GetCurrentActiveUserAllowGuest)):
    url = GetURL(url=url)
    # Check if requires access
    if url.RequiresAuth:
        user = await user()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"URL: {url} requires login.",
                headers={"WWW-Authenticate":"Bearer"}
            )
        # Check if requires group access
        #if url.RequiresGroup:
        #    in_group = False
        #    for group in url.RequiresGroup:
        #        if group in user.Groups:
        #            in_group = True
        #            break
        #    if not in_group:
        #        raise HTTPException(
        #            status_code=status.HTTP_401_UNAUTHORIZED,
        #            detail=f"You do not have access to {url}.",
        #            headers={"WWW-Authenticate":"Bearer"}
        #        )
    return url
    
@router.put("/update/url/{url}", response_model=URI)
async def UpdateURL(url: str,
                    attributes:dict,
                    description: Optional[str] = None,
                    requireAuth: Optional[bool] = None,
                    requireGroup: Optional[List[str]] = [],
                    user: User = Depends(GetCurrentActiveUser)):
    time = str(datetime.now(settings.SERVER_TIMEZONE))
    check_relationship = f"""MATCH (user:User)-[relationship]->(url:URL)
    WHERE user.UUID = "{user.UUID}"
    AND url.URL = "{url}"
    RETURN ID(user), LABELS(user), relationship
    """
    cypher = f"""MATCH (url:URL)
     WHERE url.URL = "{url}"
     SET url += $attributes
     SET url.Modifier = "{user.UUID}"
     SET url.ModifiedTime = "{time}"
    """
    if description:
        cypher += f"SET url.Description = '{description}'\n" 
    if requireAuth:
        cypher += f"SET url.RequireAuth = '{requireAuth}'\n" 
    if requireGroup:
        cypher += f"SET url.RequireGroup = '{requireGroup}'\n"
    cypher += "RETURN url"

    with settings.DB_DRIVER.session() as session:
        # Check if user owns the URL or can modify it
        if not user.Admin:
            relate = session.run(query=check_relationship).data()[0]
            if relate:
                if "OWNS" not in str(relate) and "CanModify" not in str(relate):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"You do not have write access to {url}.",
                        headers={"WWW-Authenticate":"Bearer"}
                    )
            else:
                raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"You do not have write access to {url}.",
                        headers={"WWW-Authenticate":"Bearer"}
                    )
    with settings.DB_DRIVER.session() as session:
        update = session.run(query=cypher, parameters={"attributes":attributes})
        url = update.data()[0]["url"]
    return URI(**url)

@router.get("/list/urls")
async def ListURL(limit:int=25,
                  user: User = Depends(GetCurrentActiveUserAllowGuest)):
    """ListURL returns a list of URLs
    """
    user = await user()
    if not user:
        cypher = f"""MATCH (url:URL)
        WHERE url.RequiresAuth = False
        RETURN url LIMIT {limit}
        """
    else:
        cypher = f"""MATCH (url:URL)
        RETURN url LIMIT {limit}
        """
    with settings.DB_DRIVER.session() as session:
        res = session.run(query=cypher).data()
    urls = []
    for each in res:
        print(each)
        urls.append(URI(**each["url"]))
    
    return urls

@router.post("/delete/url/{url}")
async def DeleteURL(url:str, user:User = Depends(GetCurrentActiveUser)):
    rl = GetURL(url=url)
    if rl and not rl.Creator == user.UUID:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"You do not have write access to {url}.",
                headers={"WWW-Authenticate":"Bearer"}
            )
    
    cypher = f"""MATCH (url:URL) WHERE url.URL = "{url}"
    DETACH DELETE url
    """
    with settings.DB_DRIVER.session() as session:
        result = session.run(query=cypher)
        rel = result.data()
    # rel should be empty, if not this _should_ return an error message
    return rel or {
        "response":f"URL {url} was successfully deleted."
    }