import logging
import json
import google.auth
from google.adk.tools.tool_context import ToolContext
from google.cloud import bigquery
from google.oauth2.credentials import Credentials
import google.cloud.geminidataanalytics_v1alpha as geminidataanalytics

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

def call_conversational_analytics_api(user_message: str, tool_context: ToolContext = None) -> str:
    """
    Calls the BigQuery Conversational Analytics API.
    
    Args:
        user_message: The question or message to ask the data agent.
        tool_context: The ToolContext containing runtime information.
    """
    logger.info(f"Calling Conversational Analytics API with message: {user_message} for agent: {config.bq_data_agent_id}")
    
    # Extract token similar to get_authorized_bigquery_client
    credentials = None
    auth_id = config.gemini_enterprise_auth_id
    if tool_context and tool_context.state and auth_id:
        token = tool_context.state.get(f"{auth_id}")
        if token:
            logger.info("Using Gemini Enterprise managed OAuth token from ToolContext")
            credentials = Credentials(token=token)
    
    if not credentials:
        logger.info("Falling back to Application Default Credentials (ADC) for Conversational API")
        try:
            scopes = ['https://www.googleapis.com/auth/cloud-platform']
            credentials, _ = google.auth.default(scopes=scopes)
        except Exception as e:
            logger.error(f"Error getting default credentials: {e}")
            return f"Error getting credentials: {str(e)}"
            
    if not credentials:
        return "Error: Could not obtain valid authentication credentials."

    try:
        data_chat_client = geminidataanalytics.DataChatServiceClient(credentials=credentials)
        
        messages = [
            geminidataanalytics.Message(
                user_message=geminidataanalytics.UserMessage(text=user_message)
            )
        ]
        
        data_agent_context = geminidataanalytics.DataAgentContext(
            data_agent=data_chat_client.data_agent_path(
                config.project_id, config.bq_ca_api_location, config.bq_data_agent_id
            ),
        )

        request = geminidataanalytics.ChatRequest(
            parent=f"projects/{config.project_id}/locations/{config.bq_ca_api_location}",
            messages=messages,
            data_agent_context=data_agent_context,
        )

        stream = data_chat_client.chat(request=request)
        
        responses = []
        for response in stream:
            # The SDK returns proto objects, which we can safely serialize to JSON for the LLM
            responses.append(type(response).to_json(response))
            
        return "[" + ",\n".join(responses) + "]"
        
    except Exception as e:
        logger.error(f"Error calling Conversational Analytics SDK: {e}")
        return f"Error: {e}"

def get_bigquery_tools() -> list:
    """Returns a list of custom context-aware BigQuery tools."""
    return [call_conversational_analytics_api]
