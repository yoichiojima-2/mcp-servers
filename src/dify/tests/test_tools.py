"""Tests for Dify MCP tools."""

import pytest
import yaml
from pytest_httpx import HTTPXMock

from dify.tools import (
    chat_message,
    create_dataset,
    export_dsl_workflow,
    generate_workflow_dsl,
    get_conversation_messages,
    import_dsl_workflow,
    list_documents,
    run_workflow,
    upload_document_by_text,
)


@pytest.mark.asyncio
async def test_chat_message(mock_context, httpx_mock: HTTPXMock):
    """Test sending a chat message."""
    httpx_mock.add_response(
        method="POST",
        url="https://test.dify.ai/v1/chat-messages",
        json={
            "answer": "Hello! How can I help you?",
            "conversation_id": "conv-123",
            "message_id": "msg-456",
        },
    )

    result = await chat_message(
        ctx=mock_context,
        query="Hello",
        user="test-user",
    )

    assert result == "Hello! How can I help you?"


@pytest.mark.asyncio
async def test_chat_message_with_conversation(mock_context, httpx_mock: HTTPXMock):
    """Test continuing a conversation."""
    httpx_mock.add_response(
        method="POST",
        url="https://test.dify.ai/v1/chat-messages",
        json={
            "answer": "I'm doing well, thanks!",
            "conversation_id": "conv-123",
        },
    )

    result = await chat_message(
        ctx=mock_context,
        query="How are you?",
        user="test-user",
        conversation_id="conv-123",
    )

    assert "doing well" in result


@pytest.mark.asyncio
async def test_run_workflow(mock_context, httpx_mock: HTTPXMock):
    """Test running a workflow."""
    httpx_mock.add_response(
        method="POST",
        url="https://test.dify.ai/v1/workflows/run",
        json={
            "workflow_run_id": "run-123",
            "task_id": "task-456",
            "data": {
                "outputs": {
                    "result": "Translated text"
                }
            },
        },
    )

    result = await run_workflow(
        ctx=mock_context,
        inputs={"text": "Hello", "language": "es"},
        user="test-user",
    )

    assert result["workflow_run_id"] == "run-123"
    assert "outputs" in result["data"]


@pytest.mark.asyncio
async def test_get_conversation_messages(mock_context, httpx_mock: HTTPXMock):
    """Test retrieving conversation messages."""
    httpx_mock.add_response(
        method="GET",
        url="https://test.dify.ai/v1/messages?user=test-user&conversation_id=conv-123&limit=20",
        json={
            "data": [
                {
                    "id": "msg-1",
                    "role": "user",
                    "content": "Hello",
                },
                {
                    "id": "msg-2",
                    "role": "assistant",
                    "content": "Hi there!",
                },
            ]
        },
    )

    result = await get_conversation_messages(
        ctx=mock_context,
        conversation_id="conv-123",
        user="test-user",
    )

    assert len(result) == 2
    assert result[0]["role"] == "user"
    assert result[1]["role"] == "assistant"


@pytest.mark.asyncio
async def test_create_dataset(mock_context, httpx_mock: HTTPXMock):
    """Test creating a knowledge base."""
    httpx_mock.add_response(
        method="POST",
        url="https://test.dify.ai/datasets",
        json={
            "id": "dataset-123",
            "name": "Test KB",
            "indexing_technique": "high_quality",
        },
    )

    result = await create_dataset(
        ctx=mock_context,
        name="Test KB",
        description="A test knowledge base",
    )

    assert result["id"] == "dataset-123"
    assert result["name"] == "Test KB"


@pytest.mark.asyncio
async def test_upload_document_by_text(mock_context, httpx_mock: HTTPXMock):
    """Test uploading a text document."""
    httpx_mock.add_response(
        method="POST",
        url="https://test.dify.ai/datasets/dataset-123/document/create-by-text",
        json={
            "id": "doc-456",
            "name": "Test Doc",
            "status": "indexing",
        },
    )

    result = await upload_document_by_text(
        ctx=mock_context,
        dataset_id="dataset-123",
        name="Test Doc",
        text="This is a test document.",
    )

    assert result["id"] == "doc-456"
    assert result["status"] == "indexing"


@pytest.mark.asyncio
async def test_list_documents(mock_context, httpx_mock: HTTPXMock):
    """Test listing documents in a dataset."""
    httpx_mock.add_response(
        method="GET",
        url="https://test.dify.ai/datasets/dataset-123/documents?page=1&limit=20",
        json={
            "data": [
                {"id": "doc-1", "name": "Doc 1"},
                {"id": "doc-2", "name": "Doc 2"},
            ],
            "total": 2,
        },
    )

    result = await list_documents(
        ctx=mock_context,
        dataset_id="dataset-123",
    )

    assert len(result["data"]) == 2
    assert result["total"] == 2


@pytest.mark.asyncio
async def test_import_dsl_workflow_from_content(mock_context, httpx_mock: HTTPXMock):
    """Test importing a workflow from DSL content."""
    dsl_content = """
    version: "0.1.5"
    kind: app
    app:
      name: Test Workflow
      mode: workflow
    """

    httpx_mock.add_response(
        method="POST",
        url="https://test.dify.ai/console/api/apps/imports",
        json={
            "app_id": "app-123",
            "status": "completed",
        },
    )

    result = await import_dsl_workflow(
        ctx=mock_context,
        dsl_content=dsl_content,
        name="Test Workflow",
    )

    assert result["app_id"] == "app-123"
    assert result["status"] == "completed"


@pytest.mark.asyncio
async def test_import_dsl_workflow_from_url(mock_context, httpx_mock: HTTPXMock):
    """Test importing a workflow from URL."""
    httpx_mock.add_response(
        method="POST",
        url="https://test.dify.ai/console/api/apps/imports",
        json={
            "app_id": "app-456",
            "status": "pending",
        },
    )

    result = await import_dsl_workflow(
        ctx=mock_context,
        dsl_url="https://example.com/workflow.yml",
    )

    assert result["app_id"] == "app-456"


@pytest.mark.asyncio
async def test_export_dsl_workflow(mock_context, httpx_mock: HTTPXMock):
    """Test exporting a workflow as DSL."""
    dsl_yaml = """
version: "0.1.5"
kind: app
app:
  name: Exported Workflow
  mode: workflow
"""

    httpx_mock.add_response(
        method="GET",
        url="https://test.dify.ai/console/api/apps/app-123/export?include_secret=false",
        text=dsl_yaml,
    )

    result = await export_dsl_workflow(
        ctx=mock_context,
        app_id="app-123",
    )

    assert "version" in result
    assert "Exported Workflow" in result


@pytest.mark.asyncio
async def test_generate_workflow_dsl():
    """Test generating a workflow DSL template."""
    result = await generate_workflow_dsl(
        ctx=None,  # Not needed for this function
        description="Translate text to Spanish",
        app_type="workflow",
    )

    # Parse the generated YAML
    dsl = yaml.safe_load(result)

    assert dsl["version"] == "0.1.5"
    assert dsl["kind"] == "app"
    assert dsl["app"]["mode"] == "workflow"
    assert "workflow" in dsl["app"]
    assert "nodes" in dsl["app"]["workflow"]["graph"]


@pytest.mark.asyncio
async def test_generate_workflow_dsl_with_knowledge_base():
    """Test generating a workflow with knowledge base."""
    result = await generate_workflow_dsl(
        ctx=None,
        description="Answer questions using docs",
        app_type="chatflow",
        enable_knowledge_base=True,
    )

    dsl = yaml.safe_load(result)
    nodes = dsl["app"]["workflow"]["graph"]["nodes"]

    # Check that knowledge retrieval node exists
    knowledge_nodes = [n for n in nodes if n["type"] == "knowledge-retrieval"]
    assert len(knowledge_nodes) == 1


@pytest.mark.asyncio
async def test_chat_message_streaming(mock_context, httpx_mock: HTTPXMock):
    """Test streaming chat response."""
    httpx_mock.add_response(
        method="POST",
        url="https://test.dify.ai/v1/chat-messages",
        json={
            "task_id": "task-789",
            "event": "message",
        },
    )

    result = await chat_message(
        ctx=mock_context,
        query="Tell me a story",
        user="test-user",
        response_mode="streaming",
    )

    assert "task-789" in result
    assert "Streaming" in result
