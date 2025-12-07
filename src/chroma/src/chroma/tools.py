from __future__ import annotations

import json
import os
import uuid
from pathlib import Path
from typing import TYPE_CHECKING

import chromadb

if TYPE_CHECKING:
    from chromadb import ClientAPI

from . import mcp

# ======================================================
# Client Management
# ======================================================

_client: ClientAPI | None = None


def _get_client() -> ClientAPI:
    """Get or create the ChromaDB client singleton."""
    global _client
    if _client is None:
        chroma_path = os.getenv("CHROMA_PATH", "./chroma_data")
        path = Path(chroma_path).expanduser().resolve()
        path.mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(path=str(path))
    return _client


def _generate_ids(count: int) -> list[str]:
    """Generate unique IDs for documents."""
    return [str(uuid.uuid4()) for _ in range(count)]


# ======================================================
# Collection Management
# ======================================================


@mcp.tool()
def create_collection(
    name: str,
    metadata: dict | None = None,
    get_or_create: bool = False,
) -> str:
    """
    Create a new collection.

    Args:
        name: Name of the collection
        metadata: Optional metadata for the collection
        get_or_create: If True, return existing collection if it exists

    Returns:
        Success message with collection name or error message
    """
    try:
        client = _get_client()
        if get_or_create:
            collection = client.get_or_create_collection(name=name, metadata=metadata)
            return f"Collection '{collection.name}' ready (get_or_create)"
        else:
            collection = client.create_collection(name=name, metadata=metadata)
            return f"Collection '{collection.name}' created successfully"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def list_collections() -> str:
    """
    List all collections.

    Returns:
        JSON array of collection names and metadata
    """
    try:
        client = _get_client()
        collections = client.list_collections()
        result = [
            {"name": c.name, "metadata": c.metadata}
            for c in collections
        ]
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def delete_collection(name: str) -> str:
    """
    Delete a collection.

    Args:
        name: Name of the collection to delete

    Returns:
        Success message or error message
    """
    try:
        client = _get_client()
        client.delete_collection(name=name)
        return f"Collection '{name}' deleted successfully"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def get_collection_info(name: str) -> str:
    """
    Get collection details including count and metadata.

    Args:
        name: Name of the collection

    Returns:
        JSON with collection name, count, and metadata
    """
    try:
        client = _get_client()
        collection = client.get_collection(name=name)
        result = {
            "name": collection.name,
            "count": collection.count(),
            "metadata": collection.metadata,
        }
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error: {e}"


# ======================================================
# Document CRUD
# ======================================================


@mcp.tool()
def add_documents(
    collection: str,
    documents: list[str],
    ids: list[str] | None = None,
    metadatas: list[dict] | None = None,
) -> str:
    """
    Add documents to a collection.

    Args:
        collection: Name of the collection
        documents: List of document texts to add
        ids: Optional list of IDs (auto-generated if not provided)
        metadatas: Optional list of metadata dicts for each document

    Returns:
        Success message with count or error message
    """
    try:
        client = _get_client()
        coll = client.get_collection(name=collection)

        doc_ids = ids if ids else _generate_ids(len(documents))

        coll.add(
            documents=documents,
            ids=doc_ids,
            metadatas=metadatas,
        )
        return f"Added {len(documents)} document(s) to '{collection}'"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def get_documents(
    collection: str,
    ids: list[str] | None = None,
    where: dict | None = None,
    limit: int | None = None,
    offset: int | None = None,
    include: list[str] | None = None,
) -> str:
    """
    Get documents from a collection by IDs or filters.

    Args:
        collection: Name of the collection
        ids: Optional list of specific document IDs to retrieve
        where: Optional metadata filter (e.g., {"category": "science"})
        limit: Maximum number of results
        offset: Number of results to skip
        include: What to include in results (default: ["documents", "metadatas"])

    Returns:
        JSON with documents, metadatas, and ids
    """
    try:
        client = _get_client()
        coll = client.get_collection(name=collection)

        include_fields = include if include else ["documents", "metadatas"]

        result = coll.get(
            ids=ids,
            where=where,
            limit=limit,
            offset=offset,
            include=include_fields,
        )
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def update_documents(
    collection: str,
    ids: list[str],
    documents: list[str] | None = None,
    metadatas: list[dict] | None = None,
) -> str:
    """
    Update existing documents in a collection.

    Args:
        collection: Name of the collection
        ids: List of document IDs to update
        documents: Optional new document texts
        metadatas: Optional new metadata dicts

    Returns:
        Success message or error message
    """
    try:
        client = _get_client()
        coll = client.get_collection(name=collection)

        coll.update(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )
        return f"Updated {len(ids)} document(s) in '{collection}'"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def upsert_documents(
    collection: str,
    documents: list[str],
    ids: list[str],
    metadatas: list[dict] | None = None,
) -> str:
    """
    Add or update documents (insert if not exists, update if exists).

    Args:
        collection: Name of the collection
        documents: List of document texts
        ids: List of document IDs
        metadatas: Optional list of metadata dicts

    Returns:
        Success message with count or error message
    """
    try:
        client = _get_client()
        coll = client.get_collection(name=collection)

        coll.upsert(
            documents=documents,
            ids=ids,
            metadatas=metadatas,
        )
        return f"Upserted {len(documents)} document(s) in '{collection}'"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def delete_documents(
    collection: str,
    ids: list[str] | None = None,
    where: dict | None = None,
) -> str:
    """
    Delete documents from a collection.

    Args:
        collection: Name of the collection
        ids: Optional list of document IDs to delete
        where: Optional metadata filter for deletion

    Returns:
        Success message or error message
    """
    try:
        if ids is None and where is None:
            return "Error: Must provide either 'ids' or 'where' filter"

        client = _get_client()
        coll = client.get_collection(name=collection)

        coll.delete(
            ids=ids,
            where=where,
        )
        return f"Deleted documents from '{collection}'"
    except Exception as e:
        return f"Error: {e}"


# ======================================================
# Query
# ======================================================


@mcp.tool()
def query(
    collection: str,
    query_texts: list[str],
    n_results: int = 10,
    where: dict | None = None,
    where_document: dict | None = None,
    include: list[str] | None = None,
) -> str:
    """
    Perform similarity search on a collection.

    Args:
        collection: Name of the collection to query
        query_texts: List of query texts to search for
        n_results: Number of results per query (default: 10)
        where: Optional metadata filter (e.g., {"category": "science"})
        where_document: Optional document content filter (e.g., {"$contains": "keyword"})
        include: What to include in results (default: ["documents", "metadatas", "distances"])

    Returns:
        JSON with query results including documents, metadatas, distances, and ids
    """
    try:
        client = _get_client()
        coll = client.get_collection(name=collection)

        include_fields = include if include else ["documents", "metadatas", "distances"]

        result = coll.query(
            query_texts=query_texts,
            n_results=n_results,
            where=where,
            where_document=where_document,
            include=include_fields,
        )
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error: {e}"
