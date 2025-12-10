import textwrap

from fastmcp.prompts.prompt import PromptMessage, TextContent

from . import mcp


def data_analysis_prompt(input, tools, scratchpad) -> PromptMessage:
    prompt = textwrap.dedent(
        f"""
        ## instruction
        you are a genius data scientist. your task is to answer the question based on the provided tools and data.
        use the tools effectively to gather information, perform analysis, and derive insights to answer the question accurately.

        **always add status like following at the end of your answer**
        - STATUS: DONE
        - STATUS: CONTINUE

        ## tools
        - duckdb: you can use this tool to query any database or files. the input is a SQL query. the output is the query result.
        - shell: you can use this tool to run any shell commands. the input is a shell command. the output is the command result.
        - and some math tools to help you with calculations.

        {tools}

        ## question
        {input}

        ## scratchpad
        {scratchpad}

        """
    ).strip()

    content = TextContent(
        type="text",
        text=prompt,
    )

    return PromptMessage(role="assistant", content=content)


@mcp.prompt
def data_analysis(input, tools, scratchpad) -> PromptMessage:
    return data_analysis_prompt(input, tools, scratchpad)


@mcp.tool()
def get_data_analysis_prompt(input, scratchpad, tools) -> PromptMessage:
    return data_analysis_prompt(input, tools, scratchpad)
