"""main.py

The main API server file.
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import onyx.settings as settings
import auth.auth as auth

# Setup App
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    docs_url=settings.DOCS_URL,
    redoc_url=settings.REDOC_URL,
    debug=settings.DEBUG,
    
)

# Mount static directory
if settings.USE_STATIC:
    app.mount(settings.STATIC_ROUTE,
              StaticFiles(directory=settings.STATIC_DIR),
              name="static")

# Handle templating
if settings.USE_TEMPLATES:
    templates = Jinja2Templates(directory=settings.TEMPLATE_DIR)

# Load Middleware
for ware in settings.MIDDLEWARE:
    r = ware.pop('root') # Pull the first item off
    app.add_middleware(
        r,
        **ware
    )

# Authentication Routes
app.include_router(
    auth.router,
    prefix=settings.AUTH_ENDPOINT,
    tags=["Authorization"]
)

# Root Example URL
@app.get("/")
async def root():
    """Root

    Returns the index of the API
    """
    return {"message": "Hello World"}

