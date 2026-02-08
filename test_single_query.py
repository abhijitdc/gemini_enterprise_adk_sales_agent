import asyncio
import sys
from sales_agent.agent import create_runner
from google.genai import types

async def run_test_query(query: str):
    runner = create_runner()
    session_id = "test-session-single-001"
    user_id = "test-user-single-001"
    
    print(f"Query: {query}")
    print("-" * 50)
    
    # Using runner.run_async to manage the session and execution
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=types.Content(role='user', parts=[types.Part(text=query)])
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(f"Agent: {part.text}")
    
    print("-" * 50)

if __name__ == "__main__":
    query = "Show me the top 5 customers by revenue"
    if len(sys.argv) > 1:
        query = sys.argv[1]
    asyncio.run(run_test_query(query))
