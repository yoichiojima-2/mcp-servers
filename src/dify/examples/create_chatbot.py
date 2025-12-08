"""Example: Create a RAG chatbot using the Dify MCP server.

This script demonstrates how to:
1. Create a knowledge base
2. Upload documents
3. Generate a workflow with knowledge retrieval
4. Import and test the chatbot
"""

import asyncio
import os

# Note: In actual MCP usage, these tools would be called through the MCP protocol
# This is a demonstration of the workflow

DIFY_API_KEY = os.getenv("DIFY_API_KEY")
DIFY_CONSOLE_API_KEY = os.getenv("DIFY_CONSOLE_API_KEY")


async def main():
    """Create and test a RAG chatbot."""

    print("=" * 60)
    print("Creating a RAG Chatbot with Dify MCP")
    print("=" * 60)

    # Step 1: Create knowledge base
    print("\n1. Creating knowledge base...")
    # In MCP: create_dataset(name="FAQ Database", indexing_technique="high_quality")
    print("   ✓ Knowledge base created: kb-123")

    # Step 2: Upload documents
    print("\n2. Uploading documents to knowledge base...")
    documents = [
        {
            "name": "Product FAQ",
            "text": """
            Q: How do I reset my password?
            A: Click on 'Forgot Password' on the login page and follow the instructions.

            Q: What are your support hours?
            A: We provide 24/7 support via chat and email.

            Q: How do I upgrade my plan?
            A: Go to Settings > Billing and select your desired plan.
            """,
        },
        {
            "name": "Shipping Info",
            "text": """
            We offer free shipping on orders over $50.
            Standard shipping takes 3-5 business days.
            Express shipping is available for an additional fee.
            """,
        },
    ]

    # In MCP: upload_document_by_text(dataset_id="kb-123", name=..., text=...)
    for doc in documents:
        print(f"   ✓ Uploaded: {doc['name']}")

    # Step 3: Generate workflow DSL
    print("\n3. Generating chatbot workflow...")
    # In MCP: generate_workflow_dsl(
    #     description="Customer support chatbot that answers questions using our FAQ database",
    #     app_type="chatbot",
    #     enable_knowledge_base=True
    # )
    print("   ✓ Workflow DSL generated")

    # Step 4: Customize DSL (update dataset ID)
    print("\n4. Customizing workflow configuration...")
    print("   ✓ Updated knowledge base ID to: kb-123")

    # Step 5: Import workflow
    print("\n5. Importing chatbot to Dify...")
    # In MCP: import_dsl_workflow(dsl_content=dsl_yaml, name="Support Chatbot")
    print("   ✓ Chatbot imported: app-456")

    # Step 6: Test the chatbot
    print("\n6. Testing chatbot...")
    test_queries = [
        "How do I reset my password?",
        "What are your shipping options?",
        "Do you have 24/7 support?",
    ]

    for query in test_queries:
        print(f"\n   Q: {query}")
        # In MCP: chat_message(query=query, user="test-user")
        print("   A: [Chatbot would retrieve from KB and generate response]")

    print("\n" + "=" * 60)
    print("✅ RAG Chatbot successfully created and tested!")
    print("=" * 60)
    print("\nNext steps:")
    print("- Customize the chatbot's personality in the system prompt")
    print("- Add more documents to the knowledge base")
    print("- Enable conversation features (suggested questions, opening statement)")
    print("- Deploy via API or embed in your application")


if __name__ == "__main__":
    asyncio.run(main())
