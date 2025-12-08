"""MCP Prompts (Skills) for common Dify agent patterns."""

from .server import mcp


@mcp.prompt()
def create_rag_chatbot() -> str:
    """Guide for creating a RAG (Retrieval-Augmented Generation) chatbot in Dify.

    This prompt helps you build a chatbot that can answer questions based on
    your documents and knowledge base.
    """
    return """# Creating a RAG Chatbot in Dify

This guide will help you create a chatbot that retrieves information from your knowledge base.

## Step 1: Create a Knowledge Base

Use the `create_dataset` tool to create a new knowledge base:

```
create_dataset(
    name="My Knowledge Base",
    description="Documentation for my product",
    indexing_technique="high_quality"
)
```

## Step 2: Upload Documents

Add documents to your knowledge base using `upload_document_by_text`:

```
upload_document_by_text(
    dataset_id="<dataset-id-from-step-1>",
    name="Product Guide",
    text="<your document content>"
)
```

## Step 3: Generate a RAG Workflow DSL

Create a workflow that uses knowledge retrieval:

```
generate_workflow_dsl(
    description="Answer customer questions about our product using the knowledge base",
    app_type="chatbot",
    enable_knowledge_base=True
)
```

## Step 4: Customize and Import

Take the generated DSL, customize it (update the knowledge base ID in the
knowledge retrieval node), and import it:

```
import_dsl_workflow(
    dsl_content="<customized-yaml-content>",
    name="Product Support Chatbot"
)
```

## Step 5: Test Your Chatbot

Use `chat_message` to test:

```
chat_message(
    query="How do I install the product?",
    user="test-user"
)
```

That's it! You now have a RAG chatbot that can answer questions based on your documents.
"""


@mcp.prompt()
def create_research_agent() -> str:
    """Guide for creating a multi-step research agent in Dify.

    This prompt helps you build an agent that can perform in-depth research
    by breaking down queries and retrieving information iteratively.
    """
    return """# Creating a Research Agent in Dify

Build an agent that performs comprehensive research by decomposing queries
and gathering information systematically.

## Architecture

A research agent typically includes:

1. **Query Decomposition**: Break down the research topic into sub-questions
2. **Iterative Retrieval**: Search knowledge base for each sub-question
3. **Synthesis**: Combine findings into a coherent report
4. **Refinement**: Improve based on completeness checks

## Key Components

### Conversation Variables
Store research state across turns:
- `research_theme`: Main research topic
- `sub_questions`: List of decomposed questions
- `findings`: Gathered information
- `report`: Final synthesis

### Workflow Nodes

1. **Start Node**: Accept research topic
2. **LLM Decomposition**: Generate 3-5 sub-questions
3. **Iteration Node**: Loop through sub-questions
4. **Knowledge Retrieval**: Fetch relevant documents
5. **LLM Analysis**: Analyze retrieved content
6. **Template Assembly**: Generate structured report
7. **End Node**: Output final report

## Example DSL Structure

```yaml
app:
  mode: advanced-chat
  workflow:
    graph:
      nodes:
        - id: start
          type: start
          data:
            variables:
              - variable: topic
                type: text-input

        - id: decompose
          type: llm
          data:
            prompt_template:
              - role: system
                text: "Break this research topic into 4 specific questions"
              - role: user
                text: "{{#start.topic#}}"

        - id: iterate
          type: iteration
          data:
            iterator_selector: ["decompose", "questions"]

        - id: retrieve
          type: knowledge-retrieval
          data:
            query_variable_selector: ["iterate", "item"]

        - id: analyze
          type: llm
          data:
            prompt_template:
              - role: system
                text: "Analyze and summarize the retrieved information"
              - role: user
                text: "{{#retrieve.result#}}"
```

## Best Practices

1. **Use conversation variables** to track state across multiple interactions
2. **Implement iteration nodes** for processing multiple sub-queries
3. **Add conditional branches** to handle edge cases
4. **Use template nodes** for consistent output formatting
5. **Enable retrieval reranking** for better result quality

## Getting Started

1. Export an example research workflow: `export_dsl_workflow(app_id="<example-app>")`
2. Modify the DSL to fit your needs
3. Import: `import_dsl_workflow(dsl_content="...")`
4. Test and refine

You can find example research agent DSLs in the Awesome-Dify-Workflow repository.
"""


@mcp.prompt()
def create_data_processing_workflow() -> str:
    """Guide for creating a data processing workflow in Dify.

    This prompt helps you build workflows for batch data processing,
    transformation, and analysis tasks.
    """
    return """# Creating a Data Processing Workflow in Dify

Build automated workflows for data transformation, analysis, and batch processing.

## Use Cases

- **Translation**: Batch translate documents
- **Summarization**: Generate summaries from multiple sources
- **Data Extraction**: Extract structured data from unstructured text
- **Classification**: Categorize content automatically
- **Validation**: Check data quality and consistency

## Workflow vs Chatbot

Use **Workflow** (not Chatbot) for:
- Non-conversational tasks
- Batch processing
- Deterministic operations
- No need for conversation history

## Key Features

### 1. Input Variables

Define what your workflow accepts:

```yaml
start:
  type: start
  data:
    variables:
      - variable: input_text
        type: text-input
        required: true
      - variable: target_language
        type: select
        options: ["en", "es", "fr", "de"]
```

### 2. Processing Nodes

Common node types:
- **LLM**: For AI-powered transformations
- **Code**: For programmatic processing
- **HTTP Request**: To call external APIs
- **Variable Aggregator**: Combine multiple inputs
- **If/Else**: Conditional logic
- **Template Transform**: Format output

### 3. Iteration

Process lists of items:

```yaml
iteration:
  type: iteration
  data:
    iterator_selector: ["start", "documents"]
    output_selector: ["llm", "result"]
```

### 4. Output Format

Define clear outputs:

```yaml
end:
  type: end
  data:
    outputs:
      - variable: processed_data
        value_selector: ["llm", "text"]
      - variable: metadata
        value_selector: ["code", "stats"]
```

## Example: Translation Workflow

```yaml
version: "0.1.5"
kind: app
app:
  mode: workflow
  workflow:
    graph:
      nodes:
        - id: start
          type: start
          data:
            variables:
              - variable: text
                type: paragraph
              - variable: target_lang
                type: select

        - id: translate
          type: llm
          data:
            model:
              provider: openai
              name: gpt-4
            prompt_template:
              - role: system
                text: "Translate to {{#start.target_lang#}}"
              - role: user
                text: "{{#start.text#}}"

        - id: end
          type: end
          data:
            outputs:
              - variable: translation
                value_selector: ["translate", "text"]
      edges:
        - source: start
          target: translate
        - source: translate
          target: end
```

## Quick Start

1. Generate a basic workflow:
   ```
   generate_workflow_dsl(
       description="Translate text to multiple languages",
       app_type="workflow"
   )
   ```

2. Customize the DSL with your specific logic

3. Import and test:
   ```
   import_dsl_workflow(dsl_content="<your-yaml>")
   ```

4. Execute:
   ```
   run_workflow(
       inputs={"text": "Hello", "target_lang": "es"},
       response_mode="blocking"
   )
   ```

## Best Practices

- Keep workflows focused on single tasks
- Use meaningful variable names
- Add error handling with if/else nodes
- Test with edge cases
- Document expected input/output formats
- Use code nodes for complex transformations
- Leverage templates for consistent formatting
"""


@mcp.prompt()
def create_agent_with_tools() -> str:
    """Guide for creating an AI agent with external tools in Dify.

    This prompt helps you build agents that can use tools like search,
    calculators, APIs, and custom functions.
    """
    return """# Creating an Agent with Tools in Dify

Build intelligent agents that can autonomously use tools to accomplish tasks.

## Agent Capabilities

Agents in Dify can:
- **Reason** about which tools to use
- **Make decisions** based on context
- **Call tools** sequentially or in parallel
- **Handle errors** and retry operations
- **Learn** from conversation history

## Built-in Tools

Dify provides several built-in tools:

1. **Google Search**: Search the web
2. **Wikipedia**: Query Wikipedia
3. **DuckDuckGo**: Alternative search
4. **Web Scraper**: Extract content from URLs
5. **Weather**: Get weather information
6. **Calculator**: Perform calculations
7. **Current Time**: Get current date/time

## Creating Custom Tools

You can create custom tools via:

### 1. API-based Tools

Define tools that call external APIs:

```yaml
tools:
  - type: api
    name: get_user_info
    description: Retrieve user information from database
    api:
      method: GET
      url: https://api.example.com/users/{user_id}
      headers:
        Authorization: Bearer {api_key}
```

### 2. Code-based Tools

Python functions for custom logic:

```python
def calculate_roi(investment: float, return_value: float) -> float:
    \"\"\"Calculate return on investment percentage.\"\"\"
    return ((return_value - investment) / investment) * 100
```

## Agent DSL Structure

```yaml
version: "0.1.5"
kind: app
app:
  mode: agent
  agent_config:
    strategy: function_calling
    model:
      provider: openai
      name: gpt-4
    tools:
      - provider: google
        tool_name: google_search
      - provider: wikipedia
        tool_name: wikipedia_search
    max_iterations: 5
    prompt_template:
      - role: system
        text: |
          You are a research assistant. Use available tools to find accurate
          information and provide comprehensive answers.

          Available tools:
          - Google Search: For current information
          - Wikipedia: For general knowledge

          Always cite your sources.
```

## Agent Strategies

### Function Calling (Recommended)
Uses OpenAI-style function calling:
- Best accuracy
- Most reliable
- Requires compatible models (GPT-4, Claude 3, etc.)

### ReAct (Reasoning + Acting)
Uses chain-of-thought prompting:
- More flexible
- Works with more models
- May be less accurate

## Example: Customer Service Agent

```yaml
app:
  mode: agent
  agent_config:
    strategy: function_calling
    tools:
      - name: check_order_status
        type: api
        description: Check the status of an order
        parameters:
          - name: order_id
            type: string
            required: true

      - name: search_knowledge_base
        type: dataset_retrieval
        description: Search product documentation

      - name: create_ticket
        type: api
        description: Create a support ticket

    prompt_template:
      - role: system
        text: |
          You are a customer service agent. Help customers with:
          1. Order tracking (use check_order_status)
          2. Product questions (use search_knowledge_base)
          3. Issues requiring escalation (use create_ticket)

          Be friendly, professional, and efficient.
```

## Configuration Tips

1. **Tool Selection**: Only include tools the agent actually needs
2. **Clear Descriptions**: Write clear tool descriptions for the LLM
3. **Error Handling**: Set max_iterations to prevent infinite loops
4. **Prompt Engineering**: Guide the agent on when to use each tool
5. **Testing**: Test with diverse queries to ensure proper tool usage

## Quick Start

1. Use `generate_workflow_dsl` with tools:
   ```
   generate_workflow_dsl(
       description="Research assistant that can search and summarize",
       app_type="agent",
       tools=["google_search", "wikipedia"]
   )
   ```

2. Customize the generated DSL

3. Import the agent:
   ```
   import_dsl_workflow(dsl_content="<customized-yaml>")
   ```

4. Test it:
   ```
   chat_message(
       query="What are the latest developments in quantum computing?",
       user="test-user"
   )
   ```

## Advanced: Tool Orchestration

For complex tasks, combine agent with workflow:

1. **Agent Node in Workflow**: Add an agent node to a workflow for specific subtasks
2. **Workflow as Tool**: Expose a workflow as a tool that agents can call
3. **Multi-Agent**: Chain multiple specialized agents together

This allows you to build sophisticated systems with specialized components!
"""
