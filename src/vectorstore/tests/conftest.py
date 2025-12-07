import os
import pytest
from pathlib import Path


@pytest.fixture(scope="function")
def temp_chroma_path(tmp_path):
    """Create a temporary ChromaDB path for each test."""
    chroma_path = tmp_path / "chroma_data"
    chroma_path.mkdir()

    # Set environment variable before importing tools
    os.environ["CHROMA_PATH"] = str(chroma_path)

    yield chroma_path

    # Cleanup - reset client and embedding function singletons
    from vectorstore import tools
    tools._client = None
    tools._embedding_function = None


@pytest.fixture
def sample_collection(temp_chroma_path):
    """Create a sample collection with test documents."""
    from vectorstore.tools import _get_client, _get_embedding_function

    client = _get_client()
    embedding_function = _get_embedding_function()
    collection = client.create_collection("test_collection", embedding_function=embedding_function)
    collection.add(
        documents=[
            "Document about cats and their behavior",
            "Document about dogs and training",
            "Document about birds and migration",
        ],
        metadatas=[
            {"category": "animals", "type": "feline"},
            {"category": "animals", "type": "canine"},
            {"category": "animals", "type": "avian"},
        ],
        ids=["doc1", "doc2", "doc3"],
    )
    return collection
