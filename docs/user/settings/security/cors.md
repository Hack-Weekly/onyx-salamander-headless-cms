# CORS Settings

CORS or "Cross-Origin Resource Sharing" refers to the situations when a frontend running in a browser has JavaScript code that communicates with a backend, and the backend is in a different "origin" than the frontend.

## ALLOWED_ORIGINS
Default: `[f"http://{HOST}:{PORT}",f"https://{HOST}:{PORT}"]` (List(String))

A list of origins that are allowed.

## ALLOW_METHODS
Default: `["GET","POST","PUT"]` (List(String))

A list of methods that are allowed on the API.

## ALLOW_HEADERS
Default: `["*"]` (List(String))

A list of HTTP request headers that should be supported for cross-origin requests.

## CORS_MAX_AGE
Default: `600` (Int)

The time in seconds to cache a cors request.