"""onyx/crud.py

This file handles CRUD functionality for the Neo4j database
"""
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status

# Import utilities for database access, auth, & "schemas"
from onyx import settings
from auth.auth import GetCurrentActiveUser
from models.base import Node, Nodes, Relationship
from models.user import User

# Set API Router
router = APIRouter()

@router.post("/create_node", response_model=Node)
async def CreateNode(label: str, node_attributes: dict,
                     current_user: User = Depends(GetCurrentActiveUser)):
    """CreateNode - Creates a node with label and attributes
        label: str
        node_attributes: dict
        current_user: User

        Usage:
            Accessed by route /create_node
    """
    # Check that node is not a restricted Node
    if label in settings.RESTRICTED_NODES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Operation not permitted, cannot create {label} with this method.",
            headers={"WWW-Authenticate":"Bearer"}
        )
    # Check if we are restricting the types of nodes we can create
    if settings.RESTRICT_DB:
        if label not in settings.NODE_LABELS:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Operation not permitted, cannot create {label} with this method.",
                headers={"WWW-Authenticate":"Bearer"}
            )
    # Check that attributes dictionary does not modify base fields
    unpacked = ""
    for key, value in node_attributes.items():
        if key in settings.BASE_PROPERTIES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Operation not permitted. You cannot modify those fields with this method.",
                headers={"WWW-Authenticate":"Bearer"}
            )
        if len(unpacked) > 0:
            unpacked+="\n"
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
                "attributes":node_attributes
            },
        )
        node_data = result.data()[0]
    return Node(NODE_ID=node_data["id"],
                UUID=uid,
                LABELS=node_data["labels"],
                Properties=node_data["new_node"])
# List Nodes
@router.get("/list_nodes", response_model=Nodes)
async def ListNodes(limit:int=25, current_user: User=Depends(GetCurrentActiveUser)):
    """ListNodes, lists as many nodes as requested"""
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
@router.get("/search_nodes", response_model=Nodes)
async def SearchNodes(node_property: str, property_value: str,
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
@router.put("/update/{node_id}")
async def UpdateNode(node_id: int, attributes: dict, current_user: User = Depends(GetCurrentActiveUser)):
    cypher = """MATCH (node) WHERE ID(node) = $id
    SET node += $attributes
    RETURN node, ID(node) as id, LABELS(node) as labels
    """

    with settings.DB_DRIVER.session() as session:
        result = session.run(query=cypher,
                             parameters={"id":node_id,"attributes":attributes})
        node_data = result.data()[0]
    return Node(NODE_ID=node_data["id"],
                LABELS=node_data["labels"],
                **node_data["node"])

# Delete Node
@router.post("/delete/{node_id}")
async def DeleteNode(node_id: int, current_user: User = Depends(GetCurrentActiveUser)):
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