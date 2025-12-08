# Dify MCP Examples

This directory contains example workflows and scripts demonstrating how to use the Dify MCP server.

## Examples

### 1. Simple Translator Workflow (`simple_translator.yml`)

A basic workflow that translates text to different languages.

**Import this workflow:**
```bash
# Using the import_dsl_workflow tool
import_dsl_workflow(
    dsl_url="file:///path/to/examples/simple_translator.yml",
    name="My Translator"
)
```

**Or import from GitHub:**
```bash
import_dsl_workflow(
    dsl_url="https://raw.githubusercontent.com/user/repo/main/simple_translator.yml"
)
```

**Execute the workflow:**
```bash
run_workflow(
    inputs={
        "text": "Hello, how are you?",
        "target_language": "Spanish"
    },
    response_mode="blocking"
)
```

### 2. Create RAG Chatbot (`create_chatbot.py`)

Demonstrates the complete process of creating a RAG chatbot:
- Creating a knowledge base
- Uploading documents
- Generating a workflow with knowledge retrieval
- Testing the chatbot

**Run the example:**
```bash
# Set your API keys
export DIFY_API_KEY=your-api-key
export DIFY_CONSOLE_API_KEY=your-console-key

# Run the script
uv run python examples/create_chatbot.py
```

## More Examples

For more workflow examples, check out:
- [Awesome Dify Workflows](https://github.com/svcvit/Awesome-Dify-Workflow) - Community-curated collection
- [Dify Documentation](https://docs.dify.ai) - Official examples and guides

## Using Examples with MCP

When using these examples through the MCP protocol (e.g., in Claude Desktop), you would invoke the tools like:

```
Please import the simple translator workflow from examples/simple_translator.yml
```

Claude will then use the `import_dsl_workflow` tool to import the workflow for you.

## Creating Your Own Workflows

1. Start with a template:
   ```
   generate_workflow_dsl(
       description="What you want your workflow to do",
       app_type="workflow",  # or "chatbot", "agent", "chatflow"
       enable_knowledge_base=False
   )
   ```

2. Customize the generated YAML

3. Import it:
   ```
   import_dsl_workflow(dsl_content=your_yaml)
   ```

4. Test and iterate!

## Tips

- **Start simple**: Begin with basic workflows and add complexity gradually
- **Use prompts**: The MCP prompts (skills) provide step-by-step guides for common patterns
- **Export existing workflows**: Use `export_dsl_workflow` to learn from existing Dify apps
- **Community workflows**: Browse Awesome-Dify-Workflow for inspiration
