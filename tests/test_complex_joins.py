import asyncio
import sys
import os

# Add parent directory to path to allow importing sales_agent
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sales_agent.agent import create_runner
from google.genai import types

async def run_complex_queries():
    runner = create_runner()
    session_id = "test-session-complex-001"
    user_id = "test-user-complex-001"
    
    queries = [
        "Which products have the highest total revenue, and which customers bought them most?",
        "Show me the average transaction amount for each product category in the 'APAC' region.",
        "List the top 3 customers who have spent the most on 'Electronics' products.",
        "What is the total sales revenue for each region, broken down by product name?"
    ]
    
    print(f"Running {len(queries)} complex join queries...")
    print("=" * 60)
    
    for query in queries:
        print(f"\nQUERY: {query}")
        print("-" * 30)
        
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
        
        print("-" * 60)

if __name__ == "__main__":
    asyncio.run(run_complex_queries())
