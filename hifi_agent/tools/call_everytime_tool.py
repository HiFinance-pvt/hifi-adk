from typing import Any, Dict
from google.adk.tools.tool_context import ToolContext

def call_everytime(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Call this tool every time the user message is received.
    """
    fi_data = tool_context.state.get('fi_data', {})
    print('alala', fi_data)
    return {
        'alala': 'alala'
    }