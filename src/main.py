"""main.py

The main API server file.
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
# from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.cors import CORSMiddleware
from onyx import settings
import auth.auth as auth
from onyx.routes import ImportRoutes

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
    r = ware.pop('root')  # Pull the first item off
    app.add_middleware(
        r,
        **ware
    )

# Include Routes
ImportRoutes(app)


# -----------------------------------------------THIS IS REQUIRED------------------------------------------------------------------

# to enable cors - origins contain the address of the frontend of the application so that fetch request is allowed
# origins = ["http://localhost:3000", "http://127.0.0.1:3000"]

# enabling cors and necessary headers and methods for it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000",
                   "http://127.0.0.1:3000", "localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------------------------------------------------------------

# Root Example URL


@app.get("/")
async def root():
    """Root

    Returns the index of the API
    """
    return {"message": "Hello World"}
