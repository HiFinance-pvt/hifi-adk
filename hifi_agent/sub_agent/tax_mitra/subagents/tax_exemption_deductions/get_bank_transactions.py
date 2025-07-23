from typing import List, Dict, Any
from google.adk.tools.tool_context import ToolContext


def get_bank_transactions(tool_context: ToolContext) -> List[Dict[str, Any]]:
    """
    Get bank transactions from the tool context.
    """
    return tool_context.state.get('bank_transactions', []) 