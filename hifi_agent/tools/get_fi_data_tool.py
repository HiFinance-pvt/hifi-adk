from typing import Any, Dict
from google.adk.tools.tool_context import ToolContext


def get_fi_data_tool(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Get the financial data from the tool context.
    Args:
        tool_context: ToolContext object containing the financial data
    Returns:
        Dict[str, Any] containing the financial data
    """
    fi_data = tool_context.state.get('fi_data', {})
    net_worth_data = tool_context.state.get('net_worth', {})
    credit_report_data = tool_context.state.get('credit_report', [])
    epf_details_data = tool_context.state.get('epf_details', [])
    mf_transactions_data = tool_context.state.get('mf_transactions', [])

    print('alala', net_worth_data, credit_report_data, epf_details_data, mf_transactions_data)
    return {
        "fi_data": fi_data,
        "net_worth": net_worth_data,
        "credit_report": credit_report_data,
        "epf_details": epf_details_data,
        "mf_transactions": mf_transactions_data
    }