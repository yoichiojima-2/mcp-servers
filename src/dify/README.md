# dify

MCP server for creating and managing Dify AI agents, workflows, and knowledge bases.

## Features

- **Agent & Workflow**: Import/export DSL, generate templates, support for chatbots/agents/workflows
- **Knowledge Base**: Create datasets, upload documents, list and search contents
- **Agent Interaction**: Chat messages, run workflows, conversation history
- **MCP Prompts**: Pre-built guides for RAG chatbots, research agents, data processing

## Tools

| Tool | Description |
|------|-------------|
| `chat_message` | Send messages to chatbot applications |
| `run_workflow` | Execute workflow applications |
| `get_conversation_messages` | Retrieve conversation history |
| `create_dataset` | Create a new knowledge base |
| `upload_document_by_text` | Add documents to knowledge base |
| `list_documents` | List documents in a dataset |
| `import_dsl_workflow` | Import workflow from YAML |
| `export_dsl_workflow` | Export workflow to YAML |
| `generate_workflow_dsl` | Generate workflow template from description |

## Prompts

- `create_rag_chatbot` - Build RAG chatbots step-by-step
- `create_research_agent` - Multi-step research agents
- `create_data_processing_workflow` - Batch processing workflows
- `create_agent_with_tools` - Agents with external tool access

## Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `DIFY_API_KEY` | Yes | Service API key (starts with `app-`) |
| `DIFY_CONSOLE_API_KEY` | No | Console key for import/export |
| `DIFY_BASE_URL` | No | API URL (default: `https://api.dify.ai/v1`) |
| `DIFY_CONSOLE_BASE_URL` | No | Console URL for self-hosted |

Get API keys from Dify: App Settings > API Access (service key) or Workspace Settings > API Keys (console key).

### Self-hosted Dify

```bash
DIFY_BASE_URL=http://localhost/v1
DIFY_CONSOLE_BASE_URL=http://localhost
```

## Usage

```bash
# Create .env file with API keys
cp .env.example .env

# Run server
uv run python -m dify
```

See [server guide](../../docs/server-guide.md) for common CLI options.

## Resources

- [Dify Documentation](https://docs.dify.ai)
- [Dify API Reference](https://docs.dify.ai/en/openapi-api-access-readme)
- [Awesome Dify Workflows](https://github.com/svcvit/Awesome-Dify-Workflow)
