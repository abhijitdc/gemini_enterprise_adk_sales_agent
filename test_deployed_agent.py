import vertexai
from vertexai import agent_engines
from sales_agent.config import config

def test_deployed_agent():
    if not config.agent_engine_id:
        print("Error: AGENT_ENGINE_ID is not set in .env")
        return

    print(f"Connecting to Agent Engine: {config.agent_engine_id}")
    
    try:
        vertexai.init(project=config.project_id, location=config.location)
        
        # Use vertexai.agent_engines.get for better ADK support
        remote_agent = agent_engines.get(config.agent_engine_id)
        
        # We use a schema question to verify BigQuery connectivity via ADC
        question = "What is the schema of the sales transactions table?"
        print(f"Querying agent: {question}")
        
        responses = remote_agent.stream_query(
            message=question,
            user_id="test-user-001"
        )
        
        print("\nAgent Response:")
        for response in responses:
            # ADK stream_query returns a sequence of events.
            # We look for the final model response text.
            if "content" in response and "parts" in response["content"]:
                for part in response["content"]["parts"]:
                    if "text" in part:
                        print(part["text"], end="", flush=True)
        print("\n")
        
    except Exception as e:
        print(f"Error querying agent: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_deployed_agent()
