from collections.abc import Iterable
from fastapi import FastAPI
from onyx import settings
from onyx.crud import core, page, url, file
from auth import auth

# Authentication Routes
ROUTES = [
    page.page_router,
    auth.ROUTE,
    core.ROUTE,
    url.ROUTE,
    page.ROUTE,
    file.ROUTE,
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