"""onyx/settings.py

This file holds global settings for the Onyx Salamander CMS Project.

"""
# Imports
import os
from datetime import timezone
from neo4j import GraphDatabase
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

# Main Application Settings
APP_NAME = "Onyx Salamander"
DESCRIPTION = "Headless CMS"
VERSION = "1"
DOCS_URL = "/docs"
REDOC_URL = "/redoc"
DEBUG = True  # Turn off in production
HOST = "0.0.0.0"  # IP address of host
PORT = 8000  # Port of host
SERVER_TIMEZONE = timezone.utc

# Security Settings
# Secret Key
# SECURITY WARNING: Keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "3zitWEiWeX8YyD2pYjnF9OJAxfkM_vJ_1ot6LMYKS0MNn06u2T3w6I4hXt0NWgE7hCg")

# SSL Settings
FORCE_SSL = False

# Trusted Host
ALLOWED_HOSTS = ["localhost","0.0.0.0","127.0.0.1"]

# Password Settings
FORCE_COMPLEX = True
PASSWORD_SCHEMES = ["bcrypt"]
PASSWORD_DEPRECATION = "auto"
SALT_SIZE = 32
PWD_CONTEXT = CryptContext(schemes=PASSWORD_SCHEMES,
                           deprecated=PASSWORD_DEPRECATION)

# Authentication Settings
AUTH_ENDPOINT = "/auth"
OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="auth/token")
JWT_ALGORITHM = "HS256"
TOKEN_LIFETIME_MINUTES = 15 # How many minutes an access token is valid

# Database Settings
DATABASE_URL = os.environ.get("DATABASE_URL", "neo4j://localhost:7687")
DATABASE_USER = os.environ.get("DATABASE_USER", "neo4j")
DATABASE_PASS = os.environ.get("DATABASE_PASS", "password")
# Neo4j Database Driver for convenience
DB_DRIVER = GraphDatabase.driver(DATABASE_URL,
                                 auth=(DATABASE_USER, DATABASE_PASS))
RESTRICT_DB = False # Whether to restrict database operations
RESTRICTED_NODES = ["User"] # Nodes that cannot be made through CRUD operations
NODE_LABELS = [] # List of allowed node labels
RELATIONSHIP_TYPES = [] # List of relationship types
BASE_PROPERTIES = ['CreatedBy','CreatedTime']
# Uvicorn log level
LOG_LEVEL = "info"

# What methods are allowed
ALLOW_METHODS = ["GET", "POST"]

# Response Headers
ALLOW_HEADERS = ["*"]

# CORS Settings
ALLOWED_ORIGINS = [
    f"http://{HOST}:{PORT}",
    f"https://{HOST}:{PORT}",
]

# Add debug CORS headers
if DEBUG:
    ALLOWED_ORIGINS.append(f"http://localhost:{PORT}")
    ALLOWED_ORIGINS.append(f"https://localhost:{PORT}")
    ALLOWED_ORIGINS.append("http://localhost:*")

CORS_MAX_AGE = 600  # Max time in seconds to cache cors request

# Authentication Settings
ALLOW_CREDENTIALS = True

# Allow users to access API via HTTP Basic Authentication
ENABLE_HTTP_AUTH = False

# Allow user to access API via Bearer Token Authentiation
ENABLE_BEARER_AUTH = True

# App Middleware

MIDDLEWARE = [
    {
        "root":CORSMiddleware,
        "allow_origins":ALLOWED_ORIGINS,
        "allow_credentials":ALLOW_CREDENTIALS,
        "allow_methods":ALLOW_METHODS,
        "allow_headers":ALLOW_HEADERS
    },
    {
        "root":TrustedHostMiddleware,
        "allowed_hosts":ALLOWED_HOSTS
    },
    {
        "root":GZipMiddleware,
        "minimum_size":500
    }
]
if FORCE_SSL and not DEBUG:
    MIDDLEWARE.append({"root":HTTPSRedirectMiddleware})


# HTTPSRedirectMiddleWare

# Static Files
USE_STATIC = True
STATIC_ROUTE = "/static"  # The url for accessing static files
STATIC_DIR = "static"  # The local directory for static files

# Templating
USE_TEMPLATES = True
TEMPLATE_DIR = "templates"

# Temporary File Directory
USE_TEMP_DIR = True
# Linux Systems
TEMP_DIR = "/tmp/onyx"
# Windows Systems Alternative
# import tempfile
# TEMP_DIR = tempfile.TemporaryDirectory().name
