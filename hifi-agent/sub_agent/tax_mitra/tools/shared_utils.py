from typing import Dict, Any, Union
from datetime import datetime
import re

# Tax slab definitions for AY 2025-26 (FY 2024-25)
TAX_SLABS = {
    'old': [
        (0, 300000, 0),
        (300000, 600000, 5),
        (600000, 900000, 10),
        (900000, 1200000, 15),
        (1200000, 1500000, 20),
        (1500000, float('inf'), 30)
    ],
    'new': [
        (0, 300000, 0),
        (300000, 600000, 5),
        (600000, 900000, 10),
        (900000, 1200000, 15),
        (1200000, 1500000, 20),
        (1500000, float('inf'), 30)
    ]
}

# Deduction limits
DEDUCTION_LIMITS = {
    'standard_deduction': 50000,
    '80C': 150000,
    '80D': 25000,
    '80D_parents': 25000,
    '80EEA': 200000,
    '80TTA': 10000,
    '80TTB': 50000
}

def validate_pan(pan: str) -> bool:
    """Validate PAN format."""
    if not pan or len(pan) != 10 or not pan.isalnum():
        return False
    return True

def validate_tax_regime(tax_regime: str) -> bool:
    """Validate tax regime."""
    return tax_regime in ['old', 'new']

def validate_assessment_year(assessment_year: str) -> bool:
    """Validate assessment year format."""
    if not assessment_year or assessment_year != '2025-26':
        return False
    return True

def validate_acknowledgement_number(acknowledgement_number: str) -> bool:
    """Validate ITR-V acknowledgement number format."""
    if not acknowledgement_number or not acknowledgement_number.startswith('ITR-V-'):
        return False
    try:
        year_part = acknowledgement_number.split('-')[2]
        if not year_part.isdigit() or len(year_part) != 4:
            return False
    except (IndexError, ValueError):
        return False
    return True

def convert_fi_currency_to_inr_int(fi_currency: Dict[str, Any]) -> int:
    """Converts Fi Money's currency format to an integer (INR)."""
    if not fi_currency:
        return 0
    units = int(fi_currency.get("units", "0"))
    nanos = fi_currency.get("nanos", 0)
    return units + (nanos // 1000000000)

def convert_date_fi_to_itr(fi_date: str, fi_format: str) -> str:
    """Converts date from Fi formats to YYYY-MM-DD for ITR schema."""
    if not fi_date:
        return ""
    try:
        if fi_format == "DD-MM-YYYY":
            dt_obj = datetime.strptime(fi_date, "%d-%m-%Y")
        elif fi_format == "YYYYMMDD":
            dt_obj = datetime.strptime(fi_date, "%Y%m%d")
        elif fi_format == "ISO8601":
            dt_obj = datetime.fromisoformat(fi_date.replace('Z', '+00:00'))
        else:
            return fi_date
        return dt_obj.strftime("%Y-%m-%d")
    except ValueError:
        return ""

def calculate_tax_breakdown(taxable_income: float, tax_regime: str) -> tuple:
    """Calculate tax breakdown for given taxable income and tax regime."""
    if taxable_income < 0:
        raise ValueError("Taxable income cannot be negative")
    
    slabs = TAX_SLABS.get(tax_regime)
    if not slabs:
        raise ValueError("Invalid tax regime")
    
    total_tax = 0
    tax_breakdown = []
    
    for lower, upper, rate in slabs:
        if taxable_income > lower:
            slab_amount = min(taxable_income - lower, upper - lower)
            slab_tax = slab_amount * (rate / 100)
            total_tax += slab_tax
            
            tax_breakdown.append({
                'slab': f"{lower:,.0f} - {upper if upper != float('inf') else '∞'}",
                'rate': f"{rate}%",
                'amount': slab_amount,
                'tax': slab_tax
            })
    
    return total_tax, tax_breakdown

def calculate_surcharge_and_cess(total_tax: float, taxable_income: float) -> tuple:
    """Calculate surcharge and cess."""
    surcharge = 0
    if taxable_income > 50000000:  # 50 lakhs
        surcharge = total_tax * 0.25  # 25% surcharge
    elif taxable_income > 10000000:  # 10 lakhs
        surcharge = total_tax * 0.10  # 10% surcharge
    elif taxable_income > 5000000:   # 5 lakhs
        surcharge = total_tax * 0.05  # 5% surcharge
    
    cess = (total_tax + surcharge) * 0.04
    return surcharge, cess

def apply_deductions(taxable_income: float, deductions: Dict[str, float], tax_regime: str) -> float:
    """Apply deductions to taxable income based on tax regime."""
    if tax_regime == 'old':
        total_deductions = 0
        
        # Standard deduction
        standard_deduction = deductions.get('standard_deduction', DEDUCTION_LIMITS['standard_deduction'])
        total_deductions += min(standard_deduction, taxable_income)
        
        # Chapter VI-A deductions
        chapter_6a_deductions = 0
        
        for section, limit in DEDUCTION_LIMITS.items():
            if section != 'standard_deduction':
                amount = deductions.get(section, 0)
                chapter_6a_deductions += min(amount, limit)
        
        # Other deductions
        other_deductions = deductions.get('other_deductions', 0)
        chapter_6a_deductions += other_deductions
        
        # Total deductions cannot exceed taxable income
        total_deductions += min(chapter_6a_deductions, taxable_income - total_deductions)
        
        return max(0, taxable_income - total_deductions)
    else:
        # New tax regime - only standard deduction
        standard_deduction = deductions.get('standard_deduction', DEDUCTION_LIMITS['standard_deduction'])
        return max(0, taxable_income - min(standard_deduction, taxable_income))

def categorize_income_source(income: Dict[str, Any]) -> Dict[str, Any]:
    """Categorize and process a single income source."""
    source_type = income.get('source', '').lower()
    amount = float(income.get('amount', 0))
    
    if amount <= 0:
        return None
    
    if source_type == 'salary':
        return {
            'category': 'salary_income',
            'data': {
                'employer_tan': income.get('employer_tan', ''),
                'employer_name': income.get('employer_name', ''),
                'amount': amount,
                'tds_deducted': float(income.get('tds_deducted', 0))
            }
        }
    elif source_type == 'business':
        return {
            'category': 'business_income',
            'data': {
                'business_type': income.get('business_type', ''),
                'gst_number': income.get('gst_number', ''),
                'amount': amount
            }
        }
    elif source_type == 'house_property':
        annual_value = float(income.get('annual_value', amount))
        municipal_taxes = float(income.get('municipal_taxes', 0))
        standard_deduction = annual_value * 0.30
        net_income = max(0, annual_value - municipal_taxes - standard_deduction)
        
        return {
            'category': 'house_property_income',
            'data': {
                'property_address': income.get('property_address', ''),
                'annual_value': annual_value,
                'municipal_taxes': municipal_taxes,
                'standard_deduction': standard_deduction,
                'net_income': net_income
            }
        }
    elif source_type == 'capital_gains':
        return {
            'category': 'capital_gains',
            'data': {
                'asset_type': income.get('asset_type', ''),
                'purchase_date': income.get('purchase_date', ''),
                'sale_date': income.get('sale_date', ''),
                'cost_of_acquisition': float(income.get('cost_of_acquisition', 0)),
                'sale_consideration': amount,
                'capital_gain': amount - float(income.get('cost_of_acquisition', 0))
            }
        }
    elif source_type == 'other_sources':
        return {
            'category': 'other_sources',
            'data': {
                'source_description': income.get('source_description', ''),
                'amount': amount
            }
        }
    
    return None 