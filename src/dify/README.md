# Dify MCP Server

An MCP (Model Context Protocol) server for creating and managing Dify AI agents, workflows, and knowledge bases.

## Features

### 🤖 Agent & Workflow Creation
- **Import/Export DSL**: Import and export Dify workflows as YAML
- **Generate Templates**: Auto-generate workflow DSL from natural language descriptions
- **Multiple App Types**: Support for chatbots, agents, workflows, and chatflows

### 📚 Knowledge Base Management
- **Create Datasets**: Set up knowledge bases with vector or keyword indexing
- **Upload Documents**: Add documents from text or files
- **List & Search**: Query and manage your knowledge base contents

### 💬 Agent Interaction
- **Chat Messages**: Send messages to chatbot applications
- **Run Workflows**: Execute non-conversational workflows
- **Conversation History**: Retrieve and manage conversation messages

### 🎯 MCP Prompts (Skills)
Pre-built guides for common patterns:
- **RAG Chatbot**: Build retrieval-augmented generation chatbots
- **Research Agent**: Create multi-step research agents
- **Data Processing**: Set up batch processing workflows
- **Tool-using Agents**: Build agents with external tool access

## Installation

```bash
# Clone the repository
cd src/dify

# Install dependencies with uv
uv sync

# Copy environment template
cp .env.example .env

# Edit .env with your Dify API keys
```

## Configuration

Get your API keys from Dify:

1. **Service API Key** (DIFY_API_KEY):
   - Navigate to your Dify app
   - Go to Settings > API Access
   - Create or copy an API key

2. **Console API Key** (DIFY_CONSOLE_API_KEY) - Optional:
   - Go to Workspace Settings > API Keys
   - Create a console-level API key
   - Required for importing/exporting workflows

Edit `.env`:

```bash
DIFY_API_KEY=app-your-service-api-key
DIFY_CONSOLE_API_KEY=your-console-key  # Optional
DIFY_BASE_URL=https://api.dify.ai/v1
```

For self-hosted Dify:

```bash
DIFY_BASE_URL=http://localhost/v1
DIFY_CONSOLE_BASE_URL=http://localhost
```

## Usage

### Running the Server

**Stdio mode** (for Claude Desktop):
```bash
make run
# or
uv run python -m dify
```

**SSE mode** (for web integrations):
```bash
make run-sse
# or
TRANSPORT=sse uv run python -m dify
```

**Docker**:
```bash
make docker-build
make docker-run
```

### Claude Desktop Configuration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "dify": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/mcp-servers/src/dify",
        "run",
        "python",
        "-m",
        "dify"
      ],
      "env": {
        "DIFY_API_KEY": "your-api-key",
        "DIFY_CONSOLE_API_KEY": "your-console-key"
      }
    }
  }
}
```

## Tools

### Chat & Workflow Execution

**chat_message**: Send messages to chatbot applications
```python
chat_message(
    query="What is Dify?",
    user="user-123",
    conversation_id="conv-abc"  # Optional: continue conversation
)
```

**run_workflow**: Execute workflow applications
```python
run_workflow(
    inputs={"text": "Hello", "language": "es"},
    user="user-123",
    response_mode="blocking"
)
```

**get_conversation_messages**: Retrieve conversation history
```python
get_conversation_messages(
    conversation_id="conv-abc",
    user="user-123",
    limit=20
)
```

### Knowledge Base Management

**create_dataset**: Create a new knowledge base
```python
create_dataset(
    name="Product Documentation",
    description="All product docs",
    indexing_technique="high_quality"
)
```

**upload_document_by_text**: Add documents to knowledge base
```python
upload_document_by_text(
    dataset_id="dataset-123",
    name="Installation Guide",
    text="How to install..."
)
```

**list_documents**: List all documents in a dataset
```python
list_documents(
    dataset_id="dataset-123",
    keyword="installation"
)
```

### Workflow Management

**import_dsl_workflow**: Import a workflow from YAML
```python
import_dsl_workflow(
    dsl_content="<yaml-content>",
    name="My Workflow",
    description="Does something cool"
)
```

**export_dsl_workflow**: Export a workflow to YAML
```python
export_dsl_workflow(
    app_id="app-123",
    include_secret=False
)
```

**generate_workflow_dsl**: Generate a workflow template
```python
generate_workflow_dsl(
    description="Translate documents to Spanish",
    app_type="workflow",
    enable_knowledge_base=False
)
```

## MCP Prompts

Access pre-built guides via the prompts feature:

1. **create_rag_chatbot**: Step-by-step guide for building a RAG chatbot
2. **create_research_agent**: Build multi-step research agents
3. **create_data_processing_workflow**: Set up batch processing workflows
4. **create_agent_with_tools**: Create agents with external tool access

## Examples

### Example 1: Create a RAG Chatbot

```python
# 1. Create knowledge base
kb = create_dataset(
    name="Support Docs",
    indexing_technique="high_quality"
)

# 2. Upload documents
upload_document_by_text(
    dataset_id=kb["id"],
    name="FAQ",
    text="Q: How to reset password? A: Click forgot password..."
)

# 3. Generate workflow with knowledge retrieval
dsl = generate_workflow_dsl(
    description="Answer customer questions using support docs",
    app_type="chatbot",
    enable_knowledge_base=True
)

# 4. Customize DSL (update dataset ID in knowledge node)
# ... modify YAML ...

# 5. Import the chatbot
app = import_dsl_workflow(
    dsl_content=dsl,
    name="Support Chatbot"
)

# 6. Test it
response = chat_message(
    query="How do I reset my password?",
    user="test-user"
)
```

### Example 2: Batch Translation Workflow

```python
# 1. Generate workflow DSL
dsl = generate_workflow_dsl(
    description="Translate text to multiple languages",
    app_type="workflow"
)

# 2. Import workflow
app = import_dsl_workflow(dsl_content=dsl)

# 3. Execute translation
result = run_workflow(
    inputs={
        "text": "Hello, world!",
        "target_language": "es"
    },
    response_mode="blocking"
)

print(result["data"]["outputs"]["translation"])
```

### Example 3: Export and Share a Workflow

```python
# Export your workflow
dsl_yaml = export_dsl_workflow(
    app_id="app-123",
    include_secret=False  # Don't include API keys
)

# Save to file
with open("my_workflow.yml", "w") as f:
    f.write(dsl_yaml)

# Share with others - they can import it:
import_dsl_workflow(
    dsl_url="https://example.com/my_workflow.yml"
)
```

## DSL Structure

Dify workflows are defined in YAML format (DSL):

```yaml
version: "0.1.5"
kind: app
app:
  name: My Workflow
  mode: workflow  # or: agent, advanced-chat, chatflow
  icon: 🤖
  icon_background: "#FFEAD5"

  workflow:
    graph:
      nodes:
        - id: start
          type: start
          data:
            variables:
              - variable: input_text
                type: text-input
                required: true

        - id: llm
          type: llm
          data:
            model:
              provider: openai
              name: gpt-4
            prompt_template:
              - role: system
                text: "Process this input"
              - role: user
                text: "{{#start.input_text#}}"

        - id: end
          type: end
          data:
            outputs:
              - variable: result
                value_selector: ["llm", "text"]

      edges:
        - source: start
          target: llm
        - source: llm
          target: end
```

## Node Types

Common workflow nodes:

- **start**: Entry point with input variables
- **end**: Exit point with outputs
- **llm**: LLM inference
- **knowledge-retrieval**: Search knowledge base
- **code**: Run Python code
- **http-request**: Call external APIs
- **if-else**: Conditional branching
- **iteration**: Loop over items
- **variable-aggregator**: Combine variables
- **template-transform**: Format output
- **question-classifier**: Classify user intent
- **answer**: Direct response (chatflow)

## Testing

```bash
# Run all tests
make test

# Run with coverage
uv run pytest --cov=src/dify --cov-report=html

# Run specific test
uv run pytest tests/test_tools.py::test_chat_message -v
```

## Troubleshooting

### API Key Issues

**Error: "DIFY_API_KEY not configured"**
- Ensure `.env` file exists with valid API key
- Check that key starts with `app-` for service API

**Error: "DIFY_CONSOLE_API_KEY not configured"**
- Console API key is optional but required for import/export
- Get it from Workspace Settings > API Keys

### Import/Export Issues

**Error: "Invalid YAML content"**
- Validate your YAML syntax
- Ensure version is "0.1.5"
- Check that all required fields are present

**Error: "Version mismatch"**
- Your Dify instance may be older/newer
- Try exporting a workflow from your instance to see the format

### Connection Issues

**Self-hosted Dify:**
```bash
DIFY_BASE_URL=http://localhost/v1
DIFY_CONSOLE_BASE_URL=http://localhost
```

**Cloud Dify:**
```bash
DIFY_BASE_URL=https://api.dify.ai/v1
DIFY_CONSOLE_BASE_URL=https://api.dify.ai
```

## Resources

- **Dify Documentation**: https://docs.dify.ai
- **Dify API Reference**: https://docs.dify.ai/en/openapi-api-access-readme
- **Awesome Dify Workflows**: https://github.com/svcvit/Awesome-Dify-Workflow
- **MCP Documentation**: https://modelcontextprotocol.io

## Contributing

Contributions are welcome! Please ensure:

1. All tests pass: `make test`
2. Code is formatted: `make format`
3. Code is linted: `make lint`

## License

MIT License - see LICENSE file for details

## Sources

This MCP server was built based on research from:

- [Dify API Documentation](https://docs.dify.ai/en/openapi-api-access-readme)
- [Dify Workflow API](https://deepwiki.com/langgenius/dify-docs-mintlify/3.2-workflow-api)
- [Dify Python SDK](https://pypi.org/project/dify-client/)
- [Dify DSL Documentation](https://docs.dify.ai/en/guides/application-orchestrate/creating-an-application)
- [Awesome Dify Workflows](https://github.com/svcvit/Awesome-Dify-Workflow)
