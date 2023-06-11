# Settings

## APP_NAME
Default: `"Onyx Salamander"` (String)

The application name, displayed within the API Docs

## DESCRIPTION
Default: `"Headless CMS"` (String)

The application description, displayed within the API Docs

## VERSION
Default: `1` (Int)

The API Version, used to indicate which version of Onyx CMS is being used.

## DOCS_URL
Default: `"/docs"` (String)

API documentation URL, displays the SwaggerUI generated documentation of the Onyx Salamander Headless CMS

## REDOC_URL
Default: `"/redoc"` (String)

Alternative API documentation URL, displays the ReDoc generated documentation of the Onyx Salamander Headless CMS

## DEBUG
Default: `True` (Boolean)

Flag that turn debug mode on or off.

Never deploy a site into production with DEBUG turned on!

DEBUG mode by default bypasses CORS and other security checks, and disables SSL and HTTPS redirects leaving your site vulnerable to a number of attacks. DEBUG mode should only be used for development purposes.

## HOST
Default: `"127.0.0.1"` (String)

IP Address to bind for the API Server.

## PORT
Default: `"8000"` (String)

Which port to bind for the API Server.

## SERVER_TIMEZONE
Default: ```python timezone.utc ``` (datetime.timezone)

The timezone of the server.

## LOG_LEVEL
Default: `"info"` (String)

The logging level for uvicorn.

## USE_STATIC
Default: `True` (Boolean)

Flag that enables/disables serving static content.

## STATIC_ROUTE
Default: "/static" (String)

The endpoint where static files are served from.

## STATIC_DIR
Default: "static" (String)

The folder where static files are located on the local machine.

## USE_TEMP_DIR
Default: True (Boolean)

Flag that enables/disables the use of temp directories.

## TEMP_DIR
Default: "/tmp/onyx" (String)

The folder where temporary files are located on the local machine.