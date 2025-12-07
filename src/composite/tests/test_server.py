"""Simple test to verify composite server works."""

import pytest
from composite.server import mcp


@pytest.mark.asyncio
async def test_tools_registration():
    """Test that tools from both servers are registered."""
    # Access tools through the tool manager
    tool_manager = mcp._tool_manager
    tools = tool_manager._tools

    # Access prompts through the prompt manager
    prompt_manager = mcp._prompt_manager
    prompts = prompt_manager._prompts

    print(f"\n=== Composite Server Test ===\n")
    print(f"Total tools registered: {len(tools)}")
    print(f"Total prompts registered: {len(prompts)}\n")

    # Assert that we have tools registered
    assert len(tools) > 0, "No tools registered"

    # Check for dify tools
    dify_tools = [name for name in tools.keys() if name.startswith("dify_")]
    print(f"Dify tools ({len(dify_tools)}):")
    for tool in sorted(dify_tools):
        print(f"  - {tool}")

    # Check for browser tools
    browser_tools = [name for name in tools.keys() if name.startswith("browser_")]
    print(f"\nBrowser tools ({len(browser_tools)}):")
    for tool in sorted(browser_tools):
        print(f"  - {tool}")

    # Assert that we have both dify and browser tools
    assert len(dify_tools) > 0, "No dify tools registered"
    assert len(browser_tools) > 0, "No browser tools registered"

    # Check prompts
    dify_prompts = [name for name in prompts.keys() if name.startswith("dify_")]
    browser_prompts = [name for name in prompts.keys() if name.startswith("browser_")]

    if dify_prompts:
        print(f"\nDify prompts ({len(dify_prompts)}):")
        for prompt in sorted(dify_prompts):
            print(f"  - {prompt}")

    if browser_prompts:
        print(f"\nBrowser prompts ({len(browser_prompts)}):")
        for prompt in sorted(browser_prompts):
            print(f"  - {prompt}")

    print(f"\n=== Test Complete ===\n")
