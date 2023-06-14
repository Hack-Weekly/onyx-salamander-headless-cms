"""onyx/crud.py

This file handles CRUD functionality for the Neo4j database
"""
import uuid
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status

# Import utilities for database access, auth, & "schemas"
from onyx import settings
from auth.auth import GetCurrentActiveUser
from models.base import Node, Nodes, Relationship
from models.user import User

# Set API Router
router = APIRouter()

ROUTE = {
    "router": router,
    "prefix": "/crud",
    "tags": ["CRUD"]
}


@router.post("/create/node", response_model=Node)
async def create_node(label: str,
                      node_attributes: dict,
                      current_user: User = Depends(GetCurrentActiveUser)):
    """create_node - Creates a node with label and attributes
        label: str
        node_attributes: dict
        current_user: User

        Usage:
            Accessed by route /create/node
    """
    # Check that node is not a restricted Node
    if label in settings.RESTRICTED_NODES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Operation not permitted, cannot create {label} with this method.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    # Check if we are restricting the types of nodes we can create
    if settings.RESTRICT_DB:
        if label not in settings.NODE_LABELS:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Operation not permitted, cannot create {label} with this method.",
                headers={"WWW-Authenticate": "Bearer"}
            )
    # Check that attributes dictionary does not modify base fields
    unpacked = ""
    for key, value in node_attributes.items():
        if key in settings.BASE_PROPERTIES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Operation not permitted. You cannot modify those fields with this method.",
                headers={"WWW-Authenticate": "Bearer"}
            )
        if len(unpacked) > 0:
            unpacked += "\n"
        unpacked += f"SET new_node.{key}='{value}'"
    uid = str(uuid.uuid4())

    cypher = f"""
            CREATE (new_node:{label})
            SET new_node.created_by = $created_by
            SET new_node.created_time = $created_time
            SET new_node.UUID = "{uid}"
            {unpacked}
            RETURN new_node, LABELS(new_node) as labels, ID(new_node) as id
            """
    with settings.DB_DRIVER.session() as session:
        result = session.run(
            query=cypher,
            parameters={
                "created_by": current_user.Email,
                "created_time": str(datetime.now(settings.SERVER_TIMEZONE)),
                "attributes": node_attributes
            },
        )
        node_data = result.data()[0]
    return Node(NODE_ID=node_data["id"],
                UUID=uid,
                LABELS=node_data["labels"],
                Properties=node_data["new_node"])
# List Nodes


@router.get("/list/nodes", response_model=Nodes)
async def list_nodes(limit: int = 25,
                     current_user: User = Depends(GetCurrentActiveUser)):
    """list_nodes, lists as many nodes as requested"""
    cypher = f"""MATCH (node)
    RETURN ID(node) as id, LABELS(node) as labels, node
    LIMIT {limit}"""
    with settings.DB_DRIVER.session() as session:
        result = session.run(query=cypher)
        data = result.data()
    node_list = []
    for node in data:
        print(node)
        print(node["node"])
        node = Node(NODE_ID=node["id"],
                    LABELS=node["labels"],
                    **node["node"])
        node_list.append(node)
    return Nodes(Nodes=node_list)

# Search Nodes


@router.get("/search/nodes", response_model=Nodes)
async def search_nodes(node_property: str,
                       property_value: str,
                       current_user: User = Depends(GetCurrentActiveUser)):
    """SearchNodes
    Retrieves data about a collection of nodes in the graph based on node properties
    """
    cypher = f"""
        MATCH (node)
        WHERE node.{node_property} = "{property_value}"
        RETURN ID(node) as id, LABELS(node) as labels, node
        """
    print("CYPHER:", cypher)
    with settings.DB_DRIVER.session() as session:
        result = session.run(query=cypher)
        data = result.data()

    node_list = []
    for node in data:
        node = Node(**node)
        node_list.append(node)
    return Nodes(Nodes=node_list)

# Update Node


@router.put("/update/node/{node_id}")
async def update_node(node_id: int,
                      attributes: dict,
                      current_user: User = Depends(GetCurrentActiveUser)):
    cypher = """MATCH (node) WHERE ID(node) = $id
    SET node += $attributes
    RETURN node, ID(node) as id, LABELS(node) as labels
    """

    with settings.DB_DRIVER.session() as session:
        result = session.run(query=cypher,
                             parameters={"id": node_id, "attributes": attributes})
        node_data = result.data()[0]
    return Node(NODE_ID=node_data["id"],
                LABELS=node_data["labels"],
                **node_data["node"])

# Delete Node


@router.post("/delete/node/{node_id}")
async def delete_node(node_id: int,
                      current_user: User = Depends(GetCurrentActiveUser)):
    cypher = f"""
    MATCH (node)
    WHERE ID(node) = "{node_id}"
    DETACH DELETE node
    """
    with settings.DB_DRIVER.session() as session:
        result = session.run(query=cypher)
        data = result.data()
    return data or {
        "response": f"Node with ID: {node_id} was successfully deleted from the graph."
    }

# Relationships


@router.post("/create/relationship", response_model=Relationship)
async def create_relationship(source_label: str,
                              source_property: str,
                              source_value: str,
                              target_label: str,
                              target_property: str,
                              target_value: str,
                              relationship_type: str,
                              relationship_attributes: Optional[dict] = None,
                              current_user=Depends(GetCurrentActiveUser)):
    """CreateRelationship - Creates a relationship between two nodes"""
    # Check that node is not a restricted Node
    if settings.RESTRICT_DB:
        if relationship_type not in settings.RELATIONSHIP_TYPES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Operation not permitted, relationship type not allowed.",
                headers={"WWW-Authenticate": "Bearer"}
            )
    unpacked = ""
    for key, value in relationship_attributes.items():
        if key in settings.BASE_PROPERTIES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Operation not permitted. You cannot modify those fields with this method.",
                headers={"WWW-Authenticate": "Bearer"}
            )
        if len(unpacked) > 0:
            unpacked += "\n"
        unpacked += f"SET relationship.{key}='{value}'"
    cypher = f"""
    MATCH (nodeA:{source_label}) WHERE nodeA.{source_property} = '{source_value}'
    MATCH (nodeB:{target_label}) WHERE nodeB.{target_property} = '{target_value}'
    CREATE (nodeA)-[relationship:{relationship_type}]->(nodeB)
    SET relationship.created_by = '{current_user.Email}'
    SET relationship.created_time = $created_time
    {unpacked}
    RETURN nodeA, nodeB, LABELS(nodeA), LABELS(nodeB), ID(nodeA),
    ID(nodeB), ID(relationship), TYPE(relationship), PROPERTIES(relationship)
    """

    with settings.DB_DRIVER.session() as session:
        result = session.run(query=cypher,
                             parameters={
                                 "created_time": str(datetime.now(settings.SERVER_TIMEZONE))
                             }
                             )
        rel_data = result.data()
        print(rel_data)
        rel_data = rel_data[0]
    # Convert data to nodes
    source = Node(NODE_ID=rel_data["ID(nodeA)"],
                  LABELS=rel_data["LABELS(nodeA)"],
                  **rel_data["nodeA"])
    target = Node(NODE_ID=rel_data["ID(nodeB)"],
                  LABELS=rel_data["LABELS(nodeB)"],
                  **rel_data["nodeB"])
    # Return relationship response
    return Relationship(RelationshipID=rel_data["ID(relationship)"],
                        RelationshipType=rel_data["TYPE(relationship)"],
                        Properties=rel_data["PROPERTIES(relationship)"],
                        SourceNode=source,
                        TargetNode=target)

# Read data about a relationship


@router.get("/read/relationship/{relationship_id}", response_model=Relationship)
async def read_relationship(relationship_id: int,
                            user: User = Depends(GetCurrentActiveUser)):
    cypher = f"""
    MATCH (nodeA)-[relationship]->(nodeB)
    WHERE ID(relationship) = {relationship_id}
    RETURN nodeA, ID(nodeA), LABELS(nodeA), relationship, ID(relationship),
    TYPE(relationship), nodeB, ID(nodeB), LABELS(nodeB), PROPERTIES(relationship)
    """
    with settings.DB_DRIVER.session() as session:
        result = session.run(query=cypher)
        rel_data = result.data()[0]
    # Convert data to nodes
    source = Node(NODE_ID=rel_data["ID(nodeA)"],
                  LABELS=rel_data["LABELS(nodeA)"],
                  **rel_data["nodeA"])
    target = Node(NODE_ID=rel_data["ID(nodeB)"],
                  LABELS=rel_data["LABELS(nodeB)"],
                  **rel_data["nodeB"])
    # Return relationship response
    return Relationship(RelationshipID=rel_data["ID(relationship)"],
                        RelationshipType=rel_data["TYPE(relationship)"],
                        Properties=rel_data["PROPERTIES(relationship)"],
                        SourceNode=source,
                        TargetNode=target)

# Update Relationship


@router.put("/update/relationship/{relationship_id}", response_model=Relationship)
async def update_relationship(relationship_id: int,
                              attributes: dict,
                              user: User = Depends(GetCurrentActiveUser)):
    cypher = """
    MATCH (nodeA)-[relationship]->(nodeB)
    WHERE ID(relationship) = $rel_id
    SET relationship += $attributes
    RETURN nodeA, ID(nodeA), LABELS(nodeA), relationship, ID(relationship),
    TYPE(relationship), nodeB, ID(nodeB), LABELS(nodeB), PROPERTIES(relationship)
    """
    with settings.DB_DRIVER.session() as session:
        result = session.run(query=cypher,
                             parameters={
                                 "rel_id": relationship_id,
                                 "attributes": attributes
                             })
        rel_data = result.data()[0]

    # Convert data to nodes
    source = Node(NODE_ID=rel_data["ID(nodeA)"],
                  LABELS=rel_data["LABELS(nodeA)"],
                  **rel_data["nodeA"])
    target = Node(NODE_ID=rel_data["ID(nodeB)"],
                  LABELS=rel_data["LABELS(nodeB)"],
                  **rel_data["nodeB"])
    # Return relationship response
    return Relationship(RelationshipID=rel_data["ID(relationship)"],
                        RelationshipType=rel_data["TYPE(relationship)"],
                        Properties=rel_data["PROPERTIES(relationship)"],
                        SourceNode=source,
                        TargetNode=target)

# Delete relationship


@router.post("/delete/relationship/{relationship_id}")
async def delete_relationship(relationship_id: int,
                              user: User = Depends(GetCurrentActiveUser)):
    cypher = f"""
    MATCH (nodeA)-[relationship]->(nodeB)
    WHERE ID(relationship) = {relationship_id}
    DELETE relationship
    """
    with settings.DB_DRIVER.session() as session:
        result = session.run(query=cypher)
        rel = result.data()
    # rel should be empty, if not this _should_ return an error message
    return rel or {
        "response": f"Relationship with ID: {relationship_id} was successfully deleted."
    }
