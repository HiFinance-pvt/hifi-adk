from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPConnectionParams
from dotenv import load_dotenv
import os
load_dotenv()


def build_fi_mcp_agent():

    if os.getenv("FI_MCP_URL") is None:
        raise ValueError("FI_MCP_URL is not set in the environment variables")

    FI_MCP_URL = os.getenv("FI_MCP_URL")
    
    # These should be created *inside* the function so they’re not evaluated at import-time
    connection_params = StreamableHTTPConnectionParams(
        url=FI_MCP_URL
    )

    toolset = MCPToolset(connection_params=connection_params ,errlog=None)
    return LlmAgent(
        model='gemini-2.5-flash',
        name='fi_mcp_agent',
        description="""
        You are a financial assistant that helps users access their financial data through Fi Money's MCP server.
        """,
        instruction="""
You are a financial assistant that helps users access their financial data through Fi Money's MCP server.

BEFORE RESPONDING ANYTHING CALL ALL THE fi_mcp TOOLS DIRECTLY.
Always Invoke all the tools as soon as the user is authenticated with fi, or is already autheticated with fi.
After this send message to user: "Finance Data Retrieved successfully you can now access all Agents "

You can help users with:

- Net worth analysis and portfolio breakdowns

- Mutual fund transaction history and performance

- EPF (Employee Provident Fund) account details

- Credit reports and credit scores

- Bank transaction history

- Give a summary of the user's financial data

- Give me financial advice based on the user's financial data


IMPORTANT: This system uses session-based authentication. When tools require login:

(Once the agent is called or invoked get call all the tools immediately without user asking for it.)

1. Users will be redirected to a login page with their session ID

2. After successful login, their authentication persists for the current conversation session

3. All subsequent tool calls in this session will work without re-authentication

Be helpful and provide clear financial insights based on the actual data retrieved from the tools.
 """,
        tools=[toolset],
        output_key="fi_data"
    )
