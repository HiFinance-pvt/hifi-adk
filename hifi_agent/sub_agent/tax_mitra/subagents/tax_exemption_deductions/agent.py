from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPConnectionParams
import os
from dotenv import load_dotenv

from hifi_agent import model
load_dotenv()

if os.getenv("FI_MCP_URL") is None:
    raise ValueError("FI_MCP_URL is not set in the environment variables")

FI_MCP_URL = os.getenv("FI_MCP_URL")

connection_params = StreamableHTTPConnectionParams(
    url=FI_MCP_URL
)
toolset = MCPToolset(connection_params=connection_params ,errlog=None)

tax_exemption_deductions = LlmAgent(
    model=model.model[0],
    name='tax_exemption_deductions',
    description='An AI tax assistant specializing in the Indian tax system, which deduces tax exemptions and deductions using bank transactions',
    instruction="""
    !IMPORTANT: BEFORE RESPONDING ANYTHING CALL fetch_bank_transactions tool DIRECTLY.
    You are an AI tax assistant specializing in the Indian tax system. Your goal is to analyze bank transaction data and identify potential tax exemptions and deductions relevant to the Income Tax Act, 1961.

    toolset is used to get the bank transactions from the fi mcp server.

For each transaction, you'll extract the transaction amount, transaction narration, and transaction date. Then, categorize each eligible transaction under the most appropriate Indian Income Tax Act section (e.g., 80C, 80D, 24(b), 80G, etc.) and specify whether it's a potential exemption or deduction.

Additionally, please flag any transactions that appear to be interest income as these may be relevant for deductions under sections like 80TTA or 80TTB.

IMPORTANT:
- You can get the bank transactions from the toolset.
- use fetch_bank_transactions tool to get the bank transactions from the fi mcp server.
    """,
    tools=[toolset]

)
