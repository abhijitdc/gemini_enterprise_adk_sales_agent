import logging
import sys
import os
try:
    from .config import config
except (ImportError, ValueError):
    from config import config

# Set environment variables for ADK/GenAI
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
os.environ["GOOGLE_CLOUD_PROJECT"] = config.project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = config.location

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

import google.auth
from google.adk.agents.llm_agent import Agent
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.memory.vertex_ai_memory_bank_service import VertexAiMemoryBankService
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.sessions.vertex_ai_session_service import VertexAiSessionService
from google.adk.runners import Runner
from .tools import get_bigquery_tools

    
def create_agent() -> Agent:
    """Creates the Sales Assist Agent (without runner framework)."""

    logger.info(f"Initializing agent for project: {config.project_id}")
    
    # Initialize BigQuery Tools
    bq_tools = get_bigquery_tools()

    # Create the Agent
    agent = Agent(
        name="sales_assist_agent",
        model=config.model,
        description="A helpful sales assistant that answers questions about sales transactions.",
        instruction=f"""
You are a knowledgeable Sales Assistant for the `{config.project_id}` project.
Your goal is to answer user questions about sales transactions using BigQuery data.

Workflow Guidelines:
1.  **Discovery**: If you are unsure what data is available, start by listing tables in the default dataset `{config.bigquery_table_id.rsplit('.', 1)[0]}` using `list_tables`.
2.  **Schema Inspection**: Before writing any SQL query for a table, YOU MUST inspect its schema using `get_table_schema`. This ensures you use the correct column names and types.
3.  **Data Retrieval**: Once you understand the schema, use `execute_sql` to retrieve the relevant data.
4.  **Natural Response**: Provide a clear, customer-friendly answer based on the data. If no data is found, explain why (e.g., no transactions for that date).

Important Rules:
- The default table for transactions is `{config.bigquery_table_id}`.
- ALWAYS check the schema before querying a table for the first time in a session.
- Do not make up data. If you cannot find the answer in BigQuery, say so.
        """,
        tools=bq_tools, 
    )
    
    return agent

def create_runner() -> Runner:
    """Creates a Runner with the agent and configured services."""
    global root_agent
    if root_agent is None:
        root_agent = create_agent()
    
    # Initialize Memory Service
    if config.use_agent_engine_memory and config.agent_engine_id:
        logger.info(f"Using Vertex AI Agent Engine Memory (ID: {config.agent_engine_id})")
        memory_service = VertexAiMemoryBankService(
            project=config.project_id,
            location=config.location,
            agent_engine_id=config.agent_engine_id
        )
    else:
        logger.info("Using In-Memory Memory Service (Local)")
        memory_service = InMemoryMemoryService()
        
    # Initialize Session Service
    if config.use_agent_engine_session and config.agent_engine_id:
        logger.info(f"Using Vertex AI Agent Engine Session (ID: {config.agent_engine_id})")
        session_service = VertexAiSessionService(
            project=config.project_id,
            location=config.location,
            agent_engine_id=config.agent_engine_id
        )
    else:
        logger.info("Using In-Memory Session Service (Local)")
        session_service = InMemorySessionService()
    
    runner = Runner(
        app_name="sales-assist-app",
        agent=root_agent,
        memory_service=memory_service,
        session_service=session_service,
        auto_create_session=True
    )
    
    return runner

root_agent = create_agent()

if __name__ == "__main__":
    runner = create_runner()
    print("Runner created successfully.")
