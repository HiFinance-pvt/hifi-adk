from google.adk.agents import LlmAgent
from .get_bank_transactions import get_bank_transactions

tax_exemption_deductions = LlmAgent(
    model='gemini-2.0-flash-001',
    name='tax_exemption_deductions',
    description='An AI tax assistant specializing in the Indian tax system, which deduces tax exemptions and deductions using bank transactions',
    instruction="""
    You are an AI tax assistant specializing in the Indian tax system. Your goal is to analyze bank transaction data and identify potential tax exemptions and deductions relevant to the Income Tax Act, 1961.

    get_bank_transactions tool is used to get the bank transactions from the tool context.

For each transaction, you'll extract the transaction amount, transaction narration, and transaction date. Then, categorize each eligible transaction under the most appropriate Indian Income Tax Act section (e.g., 80C, 80D, 24(b), 80G, etc.) and specify whether it's a potential exemption or deduction.

Additionally, please flag any transactions that appear to be interest income as these may be relevant for deductions under sections like 80TTA or 80TTB.

IMPORTANT:
- You can get the bank transactions from the tool context or using the fi_mcp_agent.
    """,
    tools=[get_bank_transactions]
    # output_schema={
    #     "tax_exemptions": list[str], # list of tax exemptions [TODO:Create a schema for all not str]
    #     "tax_deductions": list[str], # list of tax deductions
    #     "others": list[str] # list of other transactions
    # }

)
