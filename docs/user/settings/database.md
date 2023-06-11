# Database Settings

## DATABASE_URL
**Default**: `"neo4j://localhost:7687` (String)

## DATABASE_USER
**Default**: `"neo4j"` (String)

## DATABASE_PASS
**Default**: `"password"`

## DB_DRIVER
DB_DRIVER is a helpful `GraphDatabase.driver()` instance that allows for querying the local/remote database.

## RESTRICT_DB
**Default**: `False`

Flag that restricts database operations

## RESTRICTED_NODES
**Default**: `["User"]` (List(String))

Nodes that cannot be made through CRUD operations

## NODE_LABELS
**Default**: [] (List(String))

List of allowed node labels

## RELATIONSHIP_TYPES
**Default**: `[]` (List(String))

List of relationship types

## BASE_PROPERTIES 
**Default**: `['created_by','created_time']`

List of base properties that cannot be modified or deleted by the CRUD API endpoint.