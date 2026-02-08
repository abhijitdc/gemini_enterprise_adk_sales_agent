import asyncio
import logging
from sales_agent.config import config
from google.adk.tools.bigquery.bigquery_toolset import BigQueryToolset
from google.adk.tools.bigquery.bigquery_credentials import BigQueryCredentialsConfig
from google.adk.tools.bigquery import metadata_tool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import google.auth
from google.adk.tools.bigquery.config import BigQueryToolConfig

async def test_connection():
    logger.info(f"Testing BigQuery connection for project: {config.project_id}")
    
    # Initialize toolset directly to test authentication
    try:
        credentials, _ = google.auth.default()
        creds_config = BigQueryCredentialsConfig(credentials=credentials)
        tool_config = BigQueryToolConfig(
            compute_project_id=config.project_id,
            location=config.bigquery_location
        )
        pass

    except Exception as e:
        logger.error(f"Failed to initialize credentials config: {e}")
        return

    from sales_agent.agent import create_agent
    from sales_agent.tools import get_bigquery_toolset
    agent = create_agent()
    logger.info("Agent initialized successfully.")
    
    # We can't easily invokve 'agent.tools' directly in a simple way without a session loop 
    # if we want to test the full flow.
    # So let's just stick to `run_agent.py` for manual verification 
    # and maybe a small script that calls a tool function directly if I can import it.
    
    dataset_id = "agent_sales_data"
    table_id = "sales_transactions"
    
    logger.info(f"Attempting to fetch table info for {dataset_id}.{table_id}...")
    
    try:
        # Direct call to the underlying tool function to verify permissions
        # metadata_tool.get_table_info expects (project_id, dataset_id, table_id, credentials, settings)
        result = metadata_tool.get_table_info(
            project_id=config.project_id,
            dataset_id=dataset_id,
            table_id=table_id,
            credentials=credentials,
            settings=tool_config
        )
        logger.info("Successfully fetched table info!")
        logger.info(f"Result snippet: {str(result)[:200]}...")
    except Exception as e:
        logger.error(f"Error fetching table info: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
