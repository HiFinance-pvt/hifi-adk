from typing import Dict, Any
from .shared_utils import (
    validate_tax_regime, 
    validate_assessment_year, 
    calculate_tax_breakdown, 
    calculate_surcharge_and_cess
)

def tax_calculator(taxable_income: float, tax_regime: str, assessment_year: str) -> Dict[str, Any]:
    """
    Calculate the final tax liability based on the provided taxable income, chosen tax regime, and assessment year.
    
    Args:
        taxable_income (float): The total taxable income after deductions and exemptions
        tax_regime (str): Tax regime - 'old' or 'new'
        assessment_year (str): Assessment year (e.g., '2025-26')
    
    Returns:
        dict: Dictionary containing tax calculation details including:
            - total_tax: Total tax liability
            - tax_breakdown: Breakdown by tax slabs
            - cess: Education cess and health and education cess
            - surcharge: Surcharge if applicable
            - final_tax: Final tax amount including all components
    """
    
    # Validate inputs
    if taxable_income < 0:
        raise ValueError("Taxable income cannot be negative")
    
    if not validate_tax_regime(tax_regime):
        raise ValueError("Tax regime must be either 'old' or 'new'")
    
    if not validate_assessment_year(assessment_year):
        raise ValueError("Currently only supporting Assessment Year 2025-26")
    
    # Calculate tax breakdown using shared utility
    total_tax, tax_breakdown = calculate_tax_breakdown(taxable_income, tax_regime)
    
    # Calculate surcharge and cess using shared utility
    surcharge, cess = calculate_surcharge_and_cess(total_tax, taxable_income)
    
    # Final tax calculation
    final_tax = total_tax + surcharge + cess
    
    return {
        'taxable_income': taxable_income,
        'tax_regime': tax_regime,
        'assessment_year': assessment_year,
        'total_tax': round(total_tax, 2),
        'surcharge': round(surcharge, 2),
        'cess': round(cess, 2),
        'final_tax': round(final_tax, 2),
        'tax_breakdown': tax_breakdown
    } 