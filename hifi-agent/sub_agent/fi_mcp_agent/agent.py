# ./adk_agent_samples/mcp_agent/agent.py
import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPConnectionParams

fi_mcp_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='fi_mcp_agent',
    instruction='''You are a financial assistant that helps users access their financial data through Fi Money's MCP server. 

You can help users with:
- Net worth analysis and portfolio breakdowns
- Mutual fund transaction history and performance
- EPF (Employee Provident Fund) account details
- Credit reports and credit scores
- Bank transaction history
- Give a summary of the user's financial data
- Give me financial advice based on the user's financial data

IMPORTANT: This system uses session-based authentication. When tools require login:
1. Users will be redirected to a login page with their session ID
2. After successful login, their authentication persists for the current conversation session
3. All subsequent tool calls in this session will work without re-authentication

Be helpful and provide clear financial insights based on the actual data retrieved from the tools.''',
    tools=[
        MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url="http://localhost:8080/mcp/stream",
            ),
            # No auth_scheme needed - authentication is handled by the MCP server's middleware
            # You can filter for specific tools if needed:
            # tool_filter=['fetch_net_worth', 'fetch_credit_report']
        )
    ],
)
