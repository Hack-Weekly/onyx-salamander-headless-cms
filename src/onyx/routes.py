from collections.abc import Iterable
from fastapi import FastAPI
from onyx import settings
from onyx.crud import core
from onyx.blog import post, page, url, file, comment
from auth import auth

# Authentication Routes
ROUTES = [
    auth.ROUTE,
    post.ROUTE,
    comment.ROUTE,
    core.ROUTE,
    file.ROUTE,
    page.ROUTE,
    url.ROUTE,
    page.page_router,
]


def ImportRoutes(app: FastAPI):
    for route in ROUTES:
        if 'APIRouter' in str(type(route)):
            app.include_router(route)
        elif 'list' in str(type(route["router"])):
            for each in route["router"]:
                app.include_router(
                    each,
                    prefix=route["prefix"],
                    tags=route["tags"]
                )
        else:
            app.include_router(
                route["router"],
                prefix=route["prefix"] or None,
                tags=route["tags"] or None
            )