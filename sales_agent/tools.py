import logging
import google.auth
from google.adk.tools.tool_context import ToolContext
from google.cloud import bigquery
from google.oauth2.credentials import Credentials

try:
    from .config import config
except (ImportError, ValueError):
    from config import config

logger = logging.getLogger(__name__)

def get_authorized_bigquery_client(tool_context: ToolContext = None) -> bigquery.Client:
    """Creates a BigQuery client using either ToolContext tokens or ADC."""
    
    # 1. Check for Gemini Enterprise managed OAuth token in ToolContext
    auth_id = config.gemini_enterprise_auth_id
    if tool_context and tool_context.state and auth_id:
        token = tool_context.state.get(f"{auth_id}")
        if token:
            logger.info("Using Gemini Enterprise managed OAuth token from ToolContext")
            credentials = Credentials(token=token)
            return bigquery.Client(
                project=config.project_id,
                credentials=credentials,
                location=config.bigquery_location
            )
    
    # 2. Fallback to ADC (standard behavior)
    logger.info("Falling back to Application Default Credentials (ADC)")
    return bigquery.Client(
        project=config.project_id,
        location=config.bigquery_location
    )

def execute_sql(sql: str, tool_context: ToolContext = None) -> str:
    """
    Executes a standard SQL query in BigQuery.
    
    Use this tool ONLY after you know the table schema and column names.
    This is the primary tool for answering analytical questions and retrieving specific data points.
    
    Args:
        sql: The valid GoogleSQL query to execute.
        tool_context: The ToolContext containing runtime information.
    """
    logger.info(f"Executing SQL: {sql}")
    client = get_authorized_bigquery_client(tool_context)
    
    try:
        query_job = client.query(sql)
        results = query_job.result()
        
        # Simple string representation for the agent
        rows = [dict(row) for row in results]
        if not rows:
            return "No results found."
        return str(rows)
    except Exception as e:
        logger.error(f"Error executing BigQuery SQL: {e}")
        return f"Error executing query: {str(e)}"

def list_tables(dataset_id: str, tool_context: ToolContext = None) -> str:
    """
    Lists all available tables in a specific BigQuery dataset.
    
    Use this tool if the user's request is ambiguous or if you need to discover 
    what data is available in the project before asking for a schema or querying.
    
    Args:
        dataset_id: The full ID of the dataset (e.g., 'project.dataset_id').
        tool_context: The ToolContext containing runtime information.
    """
    logger.info(f"Listing tables in dataset: {dataset_id}")
    client = get_authorized_bigquery_client(tool_context)
    
    try:
        tables = client.list_tables(dataset_id)
        table_ids = [table.table_id for table in tables]
        if not table_ids:
            return f"No tables found in dataset {dataset_id}."
        return f"Tables in {dataset_id}: {', '.join(table_ids)}"
    except Exception as e:
        logger.error(f"Error listing tables: {e}")
        return f"Error listing tables: {str(e)}"

def get_table_schema(table_id: str, tool_context: ToolContext = None) -> str:
    """
    Retrieves the detailed schema (field names and data types) for a specific BigQuery table.
    
    ALWAYS use this tool before writing a SQL query for a table you haven't inspected yet.
    Ensures that your SQL query uses correct column names and follows the expected structure.
    
    Args:
        table_id: The full ID of the table (e.g., 'project.dataset.table_id').
        tool_context: The ToolContext containing runtime information.
    """
    logger.info(f"Getting schema for table: {table_id}")
    client = get_authorized_bigquery_client(tool_context)
    
    try:
        table = client.get_table(table_id)
        schema_info = [f"{field.name}: {field.field_type}" for field in table.schema]
        return f"Schema for {table_id}:\n" + "\n".join(schema_info)
    except Exception as e:
        logger.error(f"Error getting table schema: {e}")
        return f"Error getting table schema: {str(e)}"

def get_bigquery_tools() -> list:
    """Returns a list of custom context-aware BigQuery tools."""
    return [execute_sql, list_tables, get_table_schema]
