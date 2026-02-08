import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


@dataclass
class AgentConfig:
    project_id: str
    location: str
    bigquery_table_id: str
    bigquery_location: str
    model: str
    agent_engine_id: Optional[str] = None
    use_agent_engine_memory: bool = False
    use_agent_engine_session: bool = False
    gemini_enterprise_auth_id: Optional[str] = None

    
    @classmethod
    def from_env(cls) -> "AgentConfig":
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        location = os.getenv("GOOGLE_CLOUD_LOCATION")
        bigquery_table_id = os.getenv("BIGQUERY_TABLE_ID")
        
        if not all([project_id, location, bigquery_table_id]):
            raise ValueError("Missing required environment variables: GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION, BIGQUERY_TABLE_ID")

        return cls(
            project_id=project_id,
            location=location,
            bigquery_table_id=bigquery_table_id,
            bigquery_location=os.getenv("BIGQUERY_LOCATION", location),
            model=os.getenv("MODEL", "gemini-2.0-flash"),
            agent_engine_id=os.getenv("AGENT_ENGINE_ID"),
            use_agent_engine_memory=os.getenv("USE_AGENT_ENGINE_MEMORY", "false").lower() == "true",
            use_agent_engine_session=os.getenv("USE_AGENT_ENGINE_SESSION", "false").lower() == "true",
            gemini_enterprise_auth_id=os.getenv("GEMINI_ENTERPRISE_AUTH_ID"),
        )

# Global config instance
config = AgentConfig.from_env()
