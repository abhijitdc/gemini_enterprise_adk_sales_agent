import asyncio
import sys
from sales_agent.agent import create_runner
from google.genai import types

async def run_chat():
    runner = create_runner()
    session_id = "test-session-001"
    user_id = "test-user-001"
    
    print("Sales Assist Agent initialized (via Runner). Type 'exit' to quit.")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit"]:
                break
            
            print("Agent: Thinking...", end="\r")
            
            # Using runner.run_async to manage the session and execution
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=types.Content(role='user', parts=[types.Part(text=user_input)])
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            print(f"\nAgent: {part.text}")
            
            print("-" * 50)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\nError: {e}")

if __name__ == "__main__":
    asyncio.run(run_chat())
