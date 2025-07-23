from typing import Dict, Any
from google.adk.tools.tool_context import ToolContext
from .shared_utils import validate_tax_regime, apply_deductions

def compute_taxable_income(gross_income: float, deductions: Dict[str, float], exemptions: Dict[str, float], tax_regime: str, tool_context: ToolContext) -> float:
    """
    Compute the total taxable income by applying eligible deductions and exemptions to gross income.
    
    Args:
        gross_income (float): Total gross income from all sources
        deductions (dict): Dictionary of Chapter VI-A deductions and other deductions
            Common keys: '80C', '80D', '80G', '80EEA', '80TTA', '80TTB', 'standard_deduction'
        exemptions (dict): Dictionary of exemptions like HRA, LTA, etc.
            Common keys: 'hra_exemption', 'lta_exemption', 'transport_allowance'
        tax_regime (str): Tax regime - 'old' or 'new'
    
    Returns:
        float: Computed taxable income after applying deductions and exemptions
    """
    
    # Validate inputs
    if gross_income < 0:
        raise ValueError("Gross income cannot be negative")
    
    if not validate_tax_regime(tax_regime):
        raise ValueError("Tax regime must be either 'old' or 'new'")
    
    # Initialize taxable income
    taxable_income = gross_income
    
    # Apply exemptions first (exemptions reduce gross income)
    total_exemptions = 0
    for exemption_type, amount in exemptions.items():
        if amount > 0:
            total_exemptions += amount
    
    taxable_income -= total_exemptions
    
    # Apply deductions using shared utility
    taxable_income = apply_deductions(taxable_income, deductions, tax_regime)
    
    return round(taxable_income, 2) 