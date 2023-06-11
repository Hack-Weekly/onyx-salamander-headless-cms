# Authentication Settings

## AUTH_ENDPOINT
**Default**: `"/auth"` (String)

This string denotes the endpoint used for authentication urls.

## OAUTH2_SCHEME
**Default**: `OAuth2PasswordBearer(tokenUrl="auth/token")` (OAUTH2 Class)

This class defines the scheme used. The current version of Onyx only supports the default scheme, so change at your own risk.

## JWT_ALGORITHM
**Default**: `"HS256"` (String)

This string determines which token generation & validation algorithm will be used to generate bearer tokens.

## TOKEN_LIFETIME_MINUTES
**Default**: `15` (Int)

The number of minutes that a token is valid for.