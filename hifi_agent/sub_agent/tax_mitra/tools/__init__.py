"""
Tax Filing Tools Package

This package contains tools for Indian income tax filing and calculation.
"""

from .tax_calculator import tax_calculator
from .income_aggregator import income_aggregator
from .fill_and_submit_itr_form import fill_and_submit_itr_form
from .compute_taxable_income import compute_taxable_income
from .track_refund import track_refund
from .generate_itr_prefill_json import generate_itr_prefill_json

# Shared utilities (not exposed as tools, but available for internal use)
from .shared_utils import (
    validate_pan,
    validate_tax_regime,
    validate_assessment_year,
    validate_acknowledgement_number,
    convert_fi_currency_to_inr_int,
    convert_date_fi_to_itr,
    calculate_tax_breakdown,
    calculate_surcharge_and_cess,
    apply_deductions,
    categorize_income_source
)

__all__ = [
    'tax_calculator',
    'income_aggregator', 
    'fill_and_submit_itr_form',
    'compute_taxable_income',
    'track_refund',
    'generate_itr_prefill_json',
] 