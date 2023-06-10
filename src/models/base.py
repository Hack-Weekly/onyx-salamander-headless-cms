"""models/base.py

This file contains the base models for the NEO4J graphing database.
"""
from typing import Optional, List
from pydantic import BaseModel
#from datetime import datetime

# Auth Response Model
class Token(BaseModel):
    """Token represents a bearer token used to authenticate a user
    to the Onyx Salamander API.
    """
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """TokenData contains information about the token that is used
    to authenticate a user to the Onyx Salamander API.
    """
    Email: Optional[str] = None

# Node Response Models
class NodeBase(BaseModel):
    """NodeBase represents a 'node' in the graph database system.

    Nodes describe entities within the graph database, they can have
    zero or more labels to define what kind of node they are.

    Nodes can also have relationships which describe a connection between
    a source/parent node and a target/child node.

    In our graph, all nodes will be created with a unique UUID to allow for
    traditional "querying by id". It is imperative to use this UUID when you
    make queries of a specific object as the internal ID within the neo4j
    database is not guaranteed to be unique for each object (they are reused
    when an object is deleted.)
    """
    NODE_ID: int # Internal ID used by Neo4j, DO NOT USE FOR QUERY
    UUID: str # Unique identifier that can be used to query
    LABELS: list

class Node(NodeBase):
    """Node extends the NodeBase to allow for properties to be added to a node

    This forum post provides some useful information on when to use a label,
    property, or relationship within a node:
     https://community.neo4j.com/t/label-vs-property-what-should-i-choose/4646
    """
    Properties: Optional[dict] = None

class Nodes(BaseModel):
    """Nodes is a helper class that allows us to return a list of Nodes.
    """
    Nodes: List[Node]

# Relationship Response Models
class Relationship(BaseModel):
    """Relationship represents a relationship between two nodes.
    """
    RelationshipID: int
    RelationshipType: str
    SourceNode: Node
    TargetNode: Node
    Properties: Optional[dict] = None

# Query Response Models
class Query(BaseModel):
    """Query represents the response returned when querying the neo4j database
    """
    Response: list