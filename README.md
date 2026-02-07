# Sales Assist Agent

A powerful, AI-driven sales assistant built with the **Google Agent Development Kit (ADK)** and deployed on **Vertex AI Agent Engine**. This agent provides natural language insights into sales transaction data stored in Google BigQuery.

## Overview

The Sales Assist Agent leverages Gemini models to translate user queries into SQL, execute them against a BigQuery dataset, and provide coherent, data-driven answers. It includes advanced discovery and schema inspection tools to ensure accuracy and reliability.

## Core Features

- **BigQuery Integration**: Direct access to sales data using context-aware tools (`execute_sql`, `list_tables`, `get_table_schema`).
- **Autonomous Discovery**: The agent can list tables and inspect schemas automatically before performing queries.
- **Vertex AI Agent Engine**: Deployed as a remote reasoning engine for scalability, security, and session management.
- **Managed Authentication**: Support for **Gemini Enterprise Managed OAuth tokens** when deployed, with local fallback to Application Default Credentials (ADC).
- **Session & Memory**: Native support for persistent multi-turn conversations through Vertex AI Session/Memory services.
- **Automated Deployment**: Streamlined CI/CD via `deploy.sh`.

## Project Structure

```text
.
├── sales_agent/            # Core agent logic
│   ├── agent.py            # Agent definition and runner configuration
│   ├── config.py           # Environment variable management
│   └── tools.py            # Context-aware BigQuery tools
├── tests/                  # Unit and integration tests
├── .env.example            # Environment variable template
├── deploy.sh               # Deployment script for Vertex AI
├── run_agent.py            # Local runner for testing
├── test_agent_connection.py # Local connection validation
├── test_deployed_agent.py  # Validation for the remote agent
└── pyproject.toml          # Dependency management (uv)
```

## Prerequisites

- **Python 3.11+**
- **uv** (recommended for package management)
- **Google Cloud Project** with APIs enabled:
  - Vertex AI API
  - BigQuery API
  - Cloud Storage API
  - Discovery Engine API
- **Gemini Enterprise Auth**: Required for managed token retrieval in production.

## Configuration

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd sales-assist-agent
    ```

2.  **Initialize environment**:
    ```bash
    cp .env.example .env
    uv sync
    ```

3.  **Configurable Variables**:
    - `GOOGLE_CLOUD_PROJECT`: Your Google Cloud Project ID.
    - `GOOGLE_CLOUD_LOCATION`: Vertex AI region (e.g., `us-central1`).
    - `BIGQUERY_TABLE_ID`: Default table for queries (`project.dataset.table`).
    - `BIGQUERY_LOCATION`: (Optional) Location of the BigQuery dataset (e.g., `US`, `EU`). Defaults to `GOOGLE_CLOUD_LOCATION` if not set.
    - `MODEL`: (Optional) The Gemini model to use (e.g., `gemini-2.0-flash`).
    - `GEMINI_ENTERPRISE_AUTH_ID`: (Optional) The OAuth Client ID for Gemini Enterprise managed authentication.
    - `AGENT_ENGINE_ID`: (Optional) The ID of your deployed Agent Engine (populated after first deploy).
    - `USE_AGENT_ENGINE_MEMORY`: (Optional) Enable Vertex AI Agent Engine memory.
    - `USE_AGENT_ENGINE_SESSION`: (Optional) Enable Vertex AI Agent Engine session management.

## Deployment

Deploy using the provided script, which handles API enablement and packaging:

```bash
chmod +x deploy.sh
./deploy.sh
```

The script uses `adk deploy` to push the `sales_agent` module. After deployment, the `AGENT_ENGINE_ID` will be printed; add this to your `.env` for testing.

## Agent Workflow

The agent is instructed to follow a robust data discovery workflow:
1.  **Discover**: Use `list_tables` to see available datasets.
2.  **Inspect**: Use `get_table_schema` to verify column names and types.
3.  **Query**: Execute optimized SQL via `execute_sql`.

## Verification

### Local Testing
Verify connectivity to the agent logic and BigQuery:
```bash
uv run python test_agent_connection.py
```

### Remote Testing
Verify the deployed agent on Vertex AI:
```bash
uv run python test_deployed_agent.py
```

## Enterprise Sharing (Gemini Enterprise Web)

To share this agent as a custom tool in Gemini Enterprise Web with **per-user data security**, follow the registration process below.

### 1. Configure OAuth Credentials
Gemini Enterprise requires a Web Application Client ID to retrieve data on behalf of the user.
1.  Go to the [GCP Credentials Page](https://console.cloud.google.com/apis/credentials).
2.  Click **Create Credentials** -> **OAuth client ID**.
3.  Set **Application type** to `Web application`.
4.  Add these **Authorized redirect URIs**:
    - `https://vertexaisearch.cloud.google.com/oauth-redirect`
    - `https://vertexaisearch.cloud.google.com/static/oauth/oauth.html`
5.  Save the **Client ID**, **Client Secret**, and **Token URI**.

### 2. Add Authorization to Gemini Enterprise
1.  Open the [Gemini Enterprise Console](https://console.cloud.google.com/gemini-enterprise/).
2.  Select your App and go to the **Agents** tab.
3.  Click **Add Agent** -> **Custom agent via Agent Engine**.
4.  Under **Authorizations**, click **Add Authorization**:
    - **Name**: `sales-bq-auth` (This ID is used in code as `GEMINI_ENTERPRISE_AUTH_ID`).
    - **Client ID/Secret/Token URI**: Paste the values from step 1.
5.  Click **Done** and **Next**.

### 3. Register the Agent
1.  **Agent Name**: `Sales Assist Agent` (User-facing name).
2.  **Description**: `Answers questions about sales transactions using BigQuery data.`
3.  **Reasoning Engine Path**: Paste your Vertex AI resource path:
    `https://{GOOGLE_CLOUD_LOCATION}-aiplatform.googleapis.com/v1/projects/{GOOGLE_CLOUD_PROJECT}/locations/{GOOGLE_CLOUD_LOCATION}/reasoningEngines/{AGENT_ENGINE_ID}`
4.  Click **Create**.

### 4. Data Security & OAuth
By registering the agent with managed OAuth:
- **User Identity**: The agent executes BigQuery queries using the OAuth token of the logged-in user.
- **Data Isolation**: Users only see data they have IAM permissions to view in BigQuery.
- **Zero-Trust**: The agent never stores or shares credentials; it uses ephemeral tokens managed by Gemini Enterprise.

## Telemetry & Observability

To monitor and debug the agent's performance, you can enable OpenTelemetry tracing and logging using the following environment variables:

- `GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY`: Set to `true` to enable agent traces and logs. This provides visibility into the agent's internal operations and performance but does not include the content of prompts and responses by default.
- `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT`: Set to `true` to enable the logging of actual input prompts and output responses. This is useful for debugging the model's behavior but should be handled with care regarding data privacy.

For more information on tracing, see the [official documentation](https://cloud.google.com/agent-builder/agent-engine/manage/tracing).

## Technical Details


- **ToolContext**: All BigQuery tools are context-aware, fetching managed OAuth tokens from the `tool_context` state when available.
- **Authentication Flow**:
    - **Remote**: Uses `GEMINI_ENTERPRISE_AUTH_ID` to retrieve tokens from `ToolContext`.
    - **Local**: Automatically falls back to ADC if no session-managed tokens are found.
- **Persistence**: Swaps between `InMemory` (local) and `VertexAi` (remote) services for session and memory based on configuration.

---

*Disclaimer: This project is for demonstration purposes and should be reviewed for security best practices before production use.*

