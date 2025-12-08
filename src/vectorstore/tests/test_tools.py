import json

from vectorstore import mcp


def get_tool(name: str):
    """Get a tool function by name."""
    return mcp._tool_manager._tools[name].fn


class TestCreateCollection:
    def test_create_collection(self, temp_chroma_path):
        create_collection = get_tool("create_collection")
        result = create_collection(name="my_collection")

        assert "created successfully" in result
        assert "my_collection" in result

    def test_create_collection_with_metadata(self, temp_chroma_path):
        create_collection = get_tool("create_collection")
        result = create_collection(
            name="my_collection",
            metadata={"description": "Test collection"},
        )

        assert "created successfully" in result

    def test_create_existing_collection_error(self, temp_chroma_path):
        create_collection = get_tool("create_collection")
        create_collection(name="my_collection")

        result = create_collection(name="my_collection")
        assert "Error" in result

    def test_get_or_create(self, temp_chroma_path):
        create_collection = get_tool("create_collection")
        create_collection(name="my_collection")

        result = create_collection(name="my_collection", get_or_create=True)
        assert "ready" in result
        assert "Error" not in result


class TestListCollections:
    def test_list_empty(self, temp_chroma_path):
        list_collections = get_tool("list_collections")
        result = list_collections()

        data = json.loads(result)
        assert isinstance(data, list)
        assert len(data) == 0

    def test_list_multiple(self, temp_chroma_path):
        create_collection = get_tool("create_collection")
        create_collection(name="collection1")
        create_collection(name="collection2")

        list_collections = get_tool("list_collections")
        result = list_collections()

        data = json.loads(result)
        assert len(data) == 2
        names = [c["name"] for c in data]
        assert "collection1" in names
        assert "collection2" in names


class TestDeleteCollection:
    def test_delete_existing(self, sample_collection, temp_chroma_path):
        delete_collection = get_tool("delete_collection")
        result = delete_collection(name="test_collection")

        assert "deleted successfully" in result

        # Verify it's gone
        list_collections = get_tool("list_collections")
        data = json.loads(list_collections())
        assert len(data) == 0

    def test_delete_nonexistent(self, temp_chroma_path):
        delete_collection = get_tool("delete_collection")
        result = delete_collection(name="nonexistent")

        assert "Error" in result


class TestGetCollectionInfo:
    def test_get_info(self, sample_collection, temp_chroma_path):
        get_collection_info = get_tool("get_collection_info")
        result = get_collection_info(name="test_collection")

        data = json.loads(result)
        assert data["name"] == "test_collection"
        assert data["count"] == 3

    def test_info_nonexistent(self, temp_chroma_path):
        get_collection_info = get_tool("get_collection_info")
        result = get_collection_info(name="nonexistent")

        assert "Error" in result


class TestAddDocuments:
    def test_add_with_auto_ids(self, temp_chroma_path):
        create_collection = get_tool("create_collection")
        create_collection(name="test_collection")

        add_documents = get_tool("add_documents")
        result = add_documents(
            collection="test_collection",
            documents=["Doc 1", "Doc 2"],
        )

        assert "Added 2 document(s)" in result

    def test_add_with_custom_ids(self, temp_chroma_path):
        create_collection = get_tool("create_collection")
        create_collection(name="test_collection")

        add_documents = get_tool("add_documents")
        result = add_documents(
            collection="test_collection",
            documents=["Doc 1", "Doc 2"],
            ids=["id1", "id2"],
        )

        assert "Added 2 document(s)" in result

    def test_add_with_metadata(self, temp_chroma_path):
        create_collection = get_tool("create_collection")
        create_collection(name="test_collection")

        add_documents = get_tool("add_documents")
        result = add_documents(
            collection="test_collection",
            documents=["Doc 1"],
            ids=["id1"],
            metadatas=[{"category": "test"}],
        )

        assert "Added 1 document(s)" in result

    def test_add_to_nonexistent_collection(self, temp_chroma_path):
        add_documents = get_tool("add_documents")
        result = add_documents(
            collection="nonexistent",
            documents=["Doc 1"],
        )

        assert "Error" in result


class TestGetDocuments:
    def test_get_by_ids(self, sample_collection, temp_chroma_path):
        get_documents = get_tool("get_documents")
        result = get_documents(
            collection="test_collection",
            ids=["doc1", "doc2"],
        )

        data = json.loads(result)
        assert len(data["ids"]) == 2
        assert "doc1" in data["ids"]
        assert "doc2" in data["ids"]

    def test_get_all(self, sample_collection, temp_chroma_path):
        get_documents = get_tool("get_documents")
        result = get_documents(collection="test_collection")

        data = json.loads(result)
        assert len(data["ids"]) == 3

    def test_get_with_where_filter(self, sample_collection, temp_chroma_path):
        get_documents = get_tool("get_documents")
        result = get_documents(
            collection="test_collection",
            where={"type": "feline"},
        )

        data = json.loads(result)
        assert len(data["ids"]) == 1
        assert "doc1" in data["ids"]

    def test_get_with_limit(self, sample_collection, temp_chroma_path):
        get_documents = get_tool("get_documents")
        result = get_documents(
            collection="test_collection",
            limit=2,
        )

        data = json.loads(result)
        assert len(data["ids"]) == 2


class TestUpdateDocuments:
    def test_update_document(self, sample_collection, temp_chroma_path):
        update_documents = get_tool("update_documents")
        result = update_documents(
            collection="test_collection",
            ids=["doc1"],
            documents=["Updated document about cats"],
        )

        assert "Updated 1 document(s)" in result

        # Verify update
        get_documents = get_tool("get_documents")
        data = json.loads(get_documents(collection="test_collection", ids=["doc1"]))
        assert "Updated document" in data["documents"][0]

    def test_update_metadata(self, sample_collection, temp_chroma_path):
        update_documents = get_tool("update_documents")
        result = update_documents(
            collection="test_collection",
            ids=["doc1"],
            metadatas=[{"category": "pets", "type": "feline"}],
        )

        assert "Updated 1 document(s)" in result


class TestUpsertDocuments:
    def test_upsert_new(self, temp_chroma_path):
        create_collection = get_tool("create_collection")
        create_collection(name="test_collection")

        upsert_documents = get_tool("upsert_documents")
        result = upsert_documents(
            collection="test_collection",
            documents=["New document"],
            ids=["new_id"],
        )

        assert "Upserted 1 document(s)" in result

        # Verify insertion
        get_documents = get_tool("get_documents")
        data = json.loads(get_documents(collection="test_collection"))
        assert len(data["ids"]) == 1

    def test_upsert_existing(self, sample_collection, temp_chroma_path):
        upsert_documents = get_tool("upsert_documents")
        result = upsert_documents(
            collection="test_collection",
            documents=["Updated via upsert"],
            ids=["doc1"],
        )

        assert "Upserted 1 document(s)" in result

        # Verify update (count should still be 3)
        get_collection_info = get_tool("get_collection_info")
        data = json.loads(get_collection_info(name="test_collection"))
        assert data["count"] == 3


class TestDeleteDocuments:
    def test_delete_by_ids(self, sample_collection, temp_chroma_path):
        delete_documents = get_tool("delete_documents")
        result = delete_documents(
            collection="test_collection",
            ids=["doc1"],
        )

        assert "Deleted documents" in result

        # Verify deletion
        get_collection_info = get_tool("get_collection_info")
        data = json.loads(get_collection_info(name="test_collection"))
        assert data["count"] == 2

    def test_delete_by_where(self, sample_collection, temp_chroma_path):
        delete_documents = get_tool("delete_documents")
        result = delete_documents(
            collection="test_collection",
            where={"type": "feline"},
        )

        assert "Deleted documents" in result

        # Verify deletion
        get_collection_info = get_tool("get_collection_info")
        data = json.loads(get_collection_info(name="test_collection"))
        assert data["count"] == 2

    def test_delete_no_filter_error(self, sample_collection, temp_chroma_path):
        delete_documents = get_tool("delete_documents")
        result = delete_documents(collection="test_collection")

        assert "Error" in result
        assert "ids" in result or "where" in result


class TestQuery:
    def test_basic_query(self, sample_collection, temp_chroma_path):
        query = get_tool("query")
        result = query(
            collection="test_collection",
            query_texts=["cats"],
        )

        data = json.loads(result)
        assert "ids" in data
        assert "distances" in data
        assert len(data["ids"]) == 1
        assert len(data["ids"][0]) > 0

    def test_query_with_n_results(self, sample_collection, temp_chroma_path):
        query = get_tool("query")
        result = query(
            collection="test_collection",
            query_texts=["animals"],
            n_results=2,
        )

        data = json.loads(result)
        assert len(data["ids"][0]) == 2

    def test_query_with_where(self, sample_collection, temp_chroma_path):
        query = get_tool("query")
        result = query(
            collection="test_collection",
            query_texts=["animals"],
            n_results=10,
            where={"type": "feline"},
        )

        data = json.loads(result)
        # Should only return the cat document
        assert len(data["ids"][0]) == 1

    def test_query_with_where_document(self, sample_collection, temp_chroma_path):
        query = get_tool("query")
        result = query(
            collection="test_collection",
            query_texts=["animals"],
            n_results=10,
            where_document={"$contains": "training"},
        )

        data = json.loads(result)
        # Should only return the dog training document
        assert len(data["ids"][0]) == 1

    def test_query_empty_collection(self, temp_chroma_path):
        create_collection = get_tool("create_collection")
        create_collection(name="empty_collection")

        query = get_tool("query")
        result = query(
            collection="empty_collection",
            query_texts=["test"],
        )

        data = json.loads(result)
        assert len(data["ids"][0]) == 0

    def test_query_nonexistent_collection(self, temp_chroma_path):
        query = get_tool("query")
        result = query(
            collection="nonexistent",
            query_texts=["test"],
        )

        assert "Error" in result
