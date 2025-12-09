"""MCP Composite Server - Aggregates multiple backend MCP servers into a single endpoint."""

import os

from browser import mcp as browser_mcp
from docx import mcp as docx_mcp
from dotenv import load_dotenv
from fastmcp import FastMCP
from langquery import mcp as langquery_mcp
from pdf import mcp as pdf_mcp
from pptx_server import mcp as pptx_mcp
from vectorstore import mcp as vectorstore_mcp
from xlsx import mcp as xlsx_mcp

load_dotenv()

mcp = FastMCP(os.getenv("NAME", "composite"))

# Mount all backend MCP servers with prefixes
# Tools will be available as: lang_*, xlsx_*, pdf_*, docx_*, pptx_*, vec_*, browser_*
mcp.mount(langquery_mcp, prefix="lang")
mcp.mount(xlsx_mcp, prefix="xlsx")
mcp.mount(pdf_mcp, prefix="pdf")
mcp.mount(docx_mcp, prefix="docx")
mcp.mount(pptx_mcp, prefix="pptx")
mcp.mount(vectorstore_mcp, prefix="vec")
mcp.mount(browser_mcp, prefix="browser")


def serve():
    """Start MCP server."""
    from starlette.middleware import Middleware
    from starlette.middleware.cors import CORSMiddleware

    cors_middleware = Middleware(
        CORSMiddleware,
        allow_origins=[os.getenv("ALLOW_ORIGIN", "*")],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    transport = os.getenv("TRANSPORT", "stdio")

    if transport == "stdio":
        mcp.run(transport="stdio")
    else:
        mcp.run(
            transport=transport,
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", 8000)),
            middleware=[cors_middleware],
        )
