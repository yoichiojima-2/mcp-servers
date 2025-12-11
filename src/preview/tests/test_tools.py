"""Tests for preview server tools."""

import pytest
from fastmcp import Client

from preview import mcp
from preview.page_store import PageStore, get_store


@pytest.mark.asyncio
async def test_get_workspace_path():
    """Test get_workspace_path returns correct path."""
    async with Client(mcp) as client:
        res = await client.call_tool("get_workspace_path", {})
        path = res.content[0].text
        assert ".mcp-servers/preview" in path


@pytest.fixture(autouse=True)
def clean_store():
    """Clean the page store before each test."""
    store = get_store()
    store.clear_all()
    yield
    store.clear_all()


class TestPageStore:
    """Tests for PageStore."""

    def test_add_page(self):
        store = PageStore()
        page = store.add_page("test", "<h1>Hello</h1>", "Test Page")

        assert page.name == "test"
        assert page.content == "<h1>Hello</h1>"
        assert page.title == "Test Page"
        assert page.content_type == "html"

    def test_add_page_markdown(self):
        store = PageStore()
        page = store.add_page("readme", "# Hello", "Readme", content_type="markdown")

        assert page.content_type == "markdown"

    def test_update_page(self):
        store = PageStore()
        store.add_page("test", "<h1>Old</h1>", "Test")
        page = store.update_page("test", "<h1>New</h1>")

        assert page is not None
        assert page.content == "<h1>New</h1>"

    def test_update_nonexistent_page(self):
        store = PageStore()
        result = store.update_page("nonexistent", "content")

        assert result is None

    def test_get_page(self):
        store = PageStore()
        store.add_page("test", "<h1>Hello</h1>", "Test")
        page = store.get_page("test")

        assert page is not None
        assert page.name == "test"

    def test_get_nonexistent_page(self):
        store = PageStore()
        page = store.get_page("nonexistent")

        assert page is None

    def test_remove_page(self):
        store = PageStore()
        store.add_page("test", "<h1>Hello</h1>", "Test")

        assert store.remove_page("test") is True
        assert store.get_page("test") is None

    def test_remove_nonexistent_page(self):
        store = PageStore()

        assert store.remove_page("nonexistent") is False

    def test_clear_all(self):
        store = PageStore()
        store.add_page("page1", "content1", "Page 1")
        store.add_page("page2", "content2", "Page 2")

        count = store.clear_all()

        assert count == 2
        assert store.page_count() == 0

    def test_list_pages(self):
        store = PageStore()
        store.add_page("page1", "content1", "Page 1")
        store.add_page("page2", "content2", "Page 2")

        pages = store.list_pages()

        assert len(pages) == 2
        # Should be sorted by updated_at descending
        assert pages[0].name == "page2"

    def test_page_count(self):
        store = PageStore()

        assert store.page_count() == 0

        store.add_page("page1", "content1", "Page 1")
        assert store.page_count() == 1

        store.add_page("page2", "content2", "Page 2")
        assert store.page_count() == 2


class TestTemplates:
    """Tests for template rendering."""

    def test_render_markdown(self):
        from preview.templates import render_markdown

        html = render_markdown("# Hello\n\nWorld", "Test")

        # TOC extension adds id attribute to headers
        assert "<h1" in html and "Hello</h1>" in html
        assert "<p>World</p>" in html
        assert "<title>Test</title>" in html

    def test_render_report_dict(self):
        from preview.templates import render_report

        html = render_report({"Revenue": "$1M", "Users": "100"}, "Metrics")

        assert "Revenue" in html
        assert "$1M" in html
        assert "Users" in html
        assert "100" in html

    def test_render_report_list(self):
        from preview.templates import render_report

        data = [
            {"name": "Alice", "score": 95},
            {"name": "Bob", "score": 87},
        ]
        html = render_report(data, "Scores")

        assert "Alice" in html
        assert "95" in html
        assert "Bob" in html
        assert "87" in html

    def test_render_dashboard(self):
        from preview.templates import render_dashboard

        widgets = [
            {"title": "Users", "value": "1,234", "color": "blue"},
            {"title": "Revenue", "value": "$5M", "color": "green"},
        ]
        html = render_dashboard(widgets, "Dashboard")

        assert "Users" in html
        assert "1,234" in html
        assert "Revenue" in html
        assert "$5M" in html

    def test_highlight_code(self):
        from preview.templates import highlight_code

        html = highlight_code("print('hello')", "python")

        assert "print" in html
        assert "hello" in html


class TestHttpServer:
    """Tests for HTTP server utilities."""

    def test_inject_live_reload(self):
        from preview.http_server import inject_live_reload

        html = "<html><body><h1>Test</h1></body></html>"
        result = inject_live_reload(html)

        assert "WebSocket" in result
        assert "/livereload" in result
        assert "<h1>Test</h1>" in result

    def test_inject_live_reload_no_body(self):
        from preview.http_server import inject_live_reload

        html = "<h1>Test</h1>"
        result = inject_live_reload(html)

        assert "WebSocket" in result


@pytest.mark.asyncio
class TestMcpTools:
    """Tests for MCP tools via client."""

    async def test_serve_html(self):
        async with Client(mcp) as client:
            result = await client.call_tool(
                "serve_html",
                {"content": "<h1>Hello</h1>", "name": "test-page"},
            )

            assert "test-page" in result.content[0].text
            assert "served at" in result.content[0].text

    async def test_serve_markdown(self):
        async with Client(mcp) as client:
            result = await client.call_tool(
                "serve_markdown",
                {"content": "# Hello World", "name": "md-test"},
            )

            assert "md-test" in result.content[0].text
            assert "served at" in result.content[0].text

    async def test_list_pages_empty(self):
        async with Client(mcp) as client:
            result = await client.call_tool("list_pages", {})

            assert "No pages" in result.content[0].text

    async def test_list_pages_with_pages(self):
        async with Client(mcp) as client:
            # First serve a page
            await client.call_tool(
                "serve_html",
                {"content": "<h1>Test</h1>", "name": "list-test"},
            )

            result = await client.call_tool("list_pages", {})

            assert "list-test" in result.content[0].text

    async def test_get_page_url(self):
        async with Client(mcp) as client:
            await client.call_tool(
                "serve_html",
                {"content": "<h1>Test</h1>", "name": "url-test"},
            )

            result = await client.call_tool("get_page_url", {"name": "url-test"})

            assert "url-test" in result.content[0].text
            assert "http" in result.content[0].text

    async def test_get_page_url_not_found(self):
        async with Client(mcp) as client:
            result = await client.call_tool("get_page_url", {"name": "nonexistent"})

            assert "Error" in result.content[0].text

    async def test_update_page(self):
        async with Client(mcp) as client:
            await client.call_tool(
                "serve_html",
                {"content": "<h1>Old</h1>", "name": "update-test"},
            )

            result = await client.call_tool(
                "update_page",
                {"name": "update-test", "content": "<h1>New</h1>"},
            )

            assert "updated" in result.content[0].text

    async def test_clear_page(self):
        async with Client(mcp) as client:
            await client.call_tool(
                "serve_html",
                {"content": "<h1>Test</h1>", "name": "clear-test"},
            )

            result = await client.call_tool("clear_page", {"name": "clear-test"})

            assert "removed" in result.content[0].text

    async def test_clear_all_pages(self):
        async with Client(mcp) as client:
            await client.call_tool(
                "serve_html",
                {"content": "<h1>Test 1</h1>", "name": "clear-all-1"},
            )
            await client.call_tool(
                "serve_html",
                {"content": "<h1>Test 2</h1>", "name": "clear-all-2"},
            )

            result = await client.call_tool("clear_all_pages", {})

            assert "2" in result.content[0].text
            assert "Removed" in result.content[0].text

    async def test_serve_report(self):
        import json

        async with Client(mcp) as client:
            data = json.dumps({"Revenue": "$1M", "Users": "100"})
            result = await client.call_tool(
                "serve_report",
                {"data": data, "title": "Test Report", "name": "report-test"},
            )

            assert "report-test" in result.content[0].text
            assert "served at" in result.content[0].text

    async def test_serve_dashboard(self):
        import json

        async with Client(mcp) as client:
            widgets = json.dumps(
                [
                    {"title": "Users", "value": "100", "color": "blue"},
                ]
            )
            result = await client.call_tool(
                "serve_dashboard",
                {"widgets": widgets, "title": "Test Dashboard", "name": "dash-test"},
            )

            assert "dash-test" in result.content[0].text
            assert "served at" in result.content[0].text

    async def test_get_server_status(self):
        async with Client(mcp) as client:
            result = await client.call_tool("get_server_status", {})

            assert "Status" in result.content[0].text
            assert "URL" in result.content[0].text
