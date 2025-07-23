from typing import Dict, Any, List
from .shared_utils import categorize_income_source

async def income_aggregator(income_details: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Aggregate and categorize income from multiple sources for tax filing.
    
    Args:
        income_details (List[Dict]): List of dictionaries where each represents an income source.
            Each dict should contain:
            - source: Type of income (salary, business, house_property, capital_gains, other_sources)
            - amount: Income amount
            - Additional fields based on source type:
                - For salary: employer_tan, employer_name, tds_deducted
                - For business: business_type, gst_number
                - For house_property: property_address, annual_value, municipal_taxes
                - For capital_gains: asset_type, purchase_date, sale_date, cost_of_acquisition
                - For other_sources: source_description
    
    Returns:
        dict: Aggregated income data categorized by source types with totals and details
    """
    
    # Initialize categories
    aggregated_income = {
        'salary_income': {
            'total': 0,
            'sources': [],
            'tds_total': 0
        },
        'business_income': {
            'total': 0,
            'sources': []
        },
        'house_property_income': {
            'total': 0,
            'sources': []
        },
        'capital_gains': {
            'total': 0,
            'sources': []
        },
        'other_sources': {
            'total': 0,
            'sources': []
        },
        'gross_total_income': 0
    }
    
    # Process each income source using shared utility
    for income in income_details:
        categorized_income = categorize_income_source(income)
        if not categorized_income:
            continue
            
        category = categorized_income['category']
        data = categorized_income['data']
        
        if category == 'salary_income':
            aggregated_income['salary_income']['total'] += data['amount']
            aggregated_income['salary_income']['sources'].append(data)
            aggregated_income['salary_income']['tds_total'] += data['tds_deducted']
        elif category == 'business_income':
            aggregated_income['business_income']['total'] += data['amount']
            aggregated_income['business_income']['sources'].append(data)
        elif category == 'house_property_income':
            aggregated_income['house_property_income']['total'] += data['net_income']
            aggregated_income['house_property_income']['sources'].append(data)
        elif category == 'capital_gains':
            aggregated_income['capital_gains']['total'] += data['sale_consideration']
            aggregated_income['capital_gains']['sources'].append(data)
        elif category == 'other_sources':
            aggregated_income['other_sources']['total'] += data['amount']
            aggregated_income['other_sources']['sources'].append(data)
    
    # Calculate gross total income
    aggregated_income['gross_total_income'] = (
        aggregated_income['salary_income']['total'] +
        aggregated_income['business_income']['total'] +
        aggregated_income['house_property_income']['total'] +
        aggregated_income['capital_gains']['total'] +
        aggregated_income['other_sources']['total']
    )
    
    # Round all amounts to 2 decimal places
    for category in aggregated_income:
        if isinstance(aggregated_income[category], dict) and 'total' in aggregated_income[category]:
            aggregated_income[category]['total'] = round(aggregated_income[category]['total'], 2)
    
    aggregated_income['gross_total_income'] = round(aggregated_income['gross_total_income'], 2)
    
    return aggregated_income 