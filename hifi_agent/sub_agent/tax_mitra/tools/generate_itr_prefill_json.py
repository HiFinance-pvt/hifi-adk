# This tool function accesses Fi MCP data directly from tool_context.state.
# It assumes that the necessary Fi MCP data (net_worth, credit_report, epf_details, mf_transactions)
# has already been fetched by another mechanism and stored in the tool_context.state dictionary.

from typing import Dict, Any, List
from google.adk.tools.tool_context import ToolContext
import json
from datetime import datetime
from .shared_utils import convert_fi_currency_to_inr_int, convert_date_fi_to_itr

# --- Main Tool Function ---


async def generate_itr_prefill_json(pan: str, current_assessment_year: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Generates a comprehensive dictionary of user tax data conforming to the
    PreFillSchemaJSON_V6.5 JSON schema by utilizing pre-fetched Fi MCP data
    available in the tool_context.state.

    Args:
        pan (str): The user's Permanent Account Number (PAN).
        current_assessment_year (str): The current assessment year (e.g., "2024-25").
        tool_context (ToolContext): The context object containing pre-fetched Fi MCP data in its state.
            Expected keys in tool_context.state: "net_worth", "credit_report", "epf_details", "mf_transactions", "bank_transactions".

    Returns:
        Dict[str, Any]: A dictionary representing the pre-filled ITR JSON.
                        Includes warnings and errors if data fetching or mapping is incomplete.
    """

    # Retrieve Fi MCP data directly from tool_context.state
    net_worth_data = tool_context.state.get('net_worth', {})
    credit_report_data = tool_context.state.get('credit_report', [])
    epf_details_data = tool_context.state.get('epf_details', [])
    mf_transactions_data = tool_context.state.get('mf_transactions', [])

    itr_prefill_data: Dict[str, Any] = {}
    warnings: List[str] = []
    errors: List[str] = []

    # --- 1. Populate personalInfo ---
    itr_prefill_data["personalInfo"] = {
        "pan": pan,
        "assesseeName": {
            "surNameOrOrgName": "User", # Placeholder, as full name isn't in credit report sample
            "firstName": "Fi"
        },
        "dob": "", # Will try to derive from credit report
        "address": {
            "pinCode": 0, # Cannot derive directly from Fi MCP docs
            "emailAddress": "user@fi.money", # Placeholder
            "cityOrTownOrDistrict": "Unknown",
            "countryCode": "91", # Default to India
            "stateCode": "00", # Unknown
            "mobileNo": 0 # Unknown
        },
        "status": "I" # Individual
    }

    if credit_report_data and credit_report_data[0].get("creditReportData"):
        dob_applicant = credit_report_data[0]["creditReportData"].get("currentApplication", {}).get("currentApplicationDetails", {}).get("currentApplicantDetails", {}).get("dateOfBirthApplicant")
        if dob_applicant:
            itr_prefill_data["personalInfo"]["dob"] = convert_date_fi_to_itr(dob_applicant, "YYYYMMDD")
        else:
            warnings.append("Date of Birth not found in credit report. Please enter manually if required.")
    else:
        warnings.append("Credit report data not available, D.O.B. might be missing.")

    # --- 2. Populate filingStatus ---
    itr_prefill_data["filingStatus"] = {
        "residentialStatus": "RES", # Assuming Resident for simplicity, or could prompt user
        "returnFileSec": 11, # Common section for original return (139(1))
        "section115BA": "NA" # Assuming no specific tax regime opted
    }

    # --- 3. Populate bankAccountDtls ---
    bank_accounts_for_itr = []
    # Fi MCP net worth provides total savings account value, not individual account details (like account number, IFSC).
    # So, we can only provide a placeholder.
    if net_worth_data.get("assetValues"):
        for asset in net_worth_data["assetValues"]:
            if asset.get("assetType") == "ASSET_TYPE_SAVINGS_ACCOUNTS":
                # Assuming at least one bank account for refund, even if details are generic
                bank_accounts_for_itr.append({
                    "addtnlBankDetails": [
                        {
                            "bankAccountNo": "PLACEHOLDER_ACC_NO", # Actual account number not provided by Fi MCP doc
                            "bankName": "FI_MONEY_CONNECTED_BANK", # Generic placeholder
                            "ifsccode": "FIIN0000001", # Generic placeholder
                            "useForRefund": "true"
                        }
                    ],
                    "bankDtlsFlag": "Y"
                })
                break # Just add one bank account for demo purposes
    if not bank_accounts_for_itr:
        warnings.append("Bank account details for refund cannot be fully pre-filled from Fi MCP. Manual entry may be required.")
        itr_prefill_data["bankAccountDtls"] = [{"bankDtlsFlag": "N"}] # Indicate no bank accounts if not found/placeheld
    else:
        itr_prefill_data["bankAccountDtls"] = bank_accounts_for_itr


    # --- 4. Populate insights.cumulativeSalary (No salary data from Fi MCP) ---
    itr_prefill_data["insights"] = {
        "cumulativeSalary": {
            "salary": 0,
            "perquisitesValue": 0,
            "profitsInSalary": 0
        },
        "grossRent": 0 # Not available from Fi MCP
    }
    warnings.append("Salary income, perquisites, and profits in lieu of salary cannot be pre-filled from Fi MCP. Please enter manually.")


    # --- 5. Populate form26as (TDS/Tax Payments - partial derivation) ---
    # Fi MCP does not provide TDS details (e.g., from Form 16, 16A, 26AS).
    itr_prefill_data["form26as"] = {
        "tdsOnSalaries": {"tdsOnSalary": []},
        "tdsOnOthThanSals": {"tdSonOthThanSal": []},
        "taxPayments": {"taxPayment": [], "totalTaxPayments": 0},
        "scheduleOS": {
            "incOthThanOwnRaceHorse": {
                "dividendGross": 0, # Not directly in Fi MCP responses for dividend.
                "othersInc": {"othersIncDtls": []}
            }
        },
        "scheduleHP": {} # Not available from Fi MCP
    }
    warnings.append("TDS and advance/self-assessment tax payments cannot be pre-filled from Fi MCP. These usually come from Form 26AS.")


    # --- 6. Populate Mutual Fund (MF) related sections (Schedule 112A for LTCG on Equity/MF) ---
    # This is a highly simplified placeholder. Full LTCG calculation requires cost basis, acquisition date,
    # FMV as of 31-Jan-2018 for equity, and depends on whether STT was paid for equity funds.
    # Fi MCP provides transaction history, but not the calculated capital gain itself for tax purposes.
    if mf_transactions_data:
        # For demonstration, let's assume a simplified total for Schedule 112A
        # In a real system, you'd calculate actual gains based on FIFO/LIFO, dates, etc.
        total_mf_market_value = 0
        if net_worth_data.get("assetValues"):
            for asset in net_worth_data["assetValues"]:
                if asset.get("assetType") == "ASSET_TYPE_MUTUAL_FUND":
                    total_mf_market_value = convert_fi_currency_to_inr_int(asset.get("totalValue"))
                    break
        
        # Placeholder values for LTCG
        assumed_acquisition_cost = int(total_mf_market_value * 0.9) # Assume 10% gain
        assumed_ltcg = total_mf_market_value - assumed_acquisition_cost

        itr_prefill_data["ais"] = {
            "schedule112A": {
                "schedule112ADtls": [
                    {
                        "ISINCode": "INNOTREQUIRD", # Per schema, for post-Jan 2018 transactions
                        "shareUnitName": "CONSOLIDATED", # Consolidated for simplicity
                        "acquisitionCost": assumed_acquisition_cost,
                        "fullValueConsdr": total_mf_market_value,
                        "ltcgBeforelowerB1B2": assumed_ltcg
                    }
                ]
            }
        }
        warnings.append("Mutual fund capital gains (Schedule 112A) are estimated based on current value. Actual calculation with transaction history and cost basis is required for accurate filing.")
    else:
        warnings.append("No mutual fund transaction data available from Fi MCP for capital gains pre-fill.")


    # --- 7. Populate EPF details for relevant sections (e.g., balance sheet values for ITR3/4) ---
    if epf_details_data:
        epf_balance = convert_fi_currency_to_inr_int(epf_details_data[0]["rawDetails"]["overall_pf_balance"]["current_pf_balance"])
        
        # EPF is a long-term investment. Mapping to form3CD balance sheet for a business/professional
        # This is for ITR3/4 where balance sheet is required.
        itr_prefill_data.setdefault("form3CD", {}).setdefault("partABS", {}).setdefault("fundApply", {}).setdefault("investments", {}).setdefault("longTermInv", {})["others"] = epf_balance

        # If EPF interest/contributions need to be shown in P&L, it's more complex.
        # Assuming EPF contributions/interest don't directly map to P&L items for ITR pre-fill unless withdrawn.
        warnings.append("EPF balance is included in investments. Detailed EPF contributions/interest/withdrawal income not fully pre-filled without explicit mappings to P&L items.")
    else:
        warnings.append("EPF details not available from Fi MCP for pre-fill.")


    # --- 8. Populate Net Worth related sections (Schedule AL - Assets and Liabilities) ---
    # Schedule AL requires break-down by asset type, acquisition cost, and sometimes addresses.
    # Fi MCP provides aggregated values. We will map them to logical categories.
    
    itr_prefill_data.setdefault("scheduleAL", {})["movableAsset"] = {
        "cashInHand": 0, # Not provided by Fi MCP
        "depositsInBank": 0,
        "sharesAndSecurities": 0,
        "jewelleryBullionEtc": 0, # Not provided by Fi MCP
        "loansAndAdvancesGiven": 0, # Not provided by Fi MCP
        "insurancePolicies": 0, # Not provided by Fi MCP
        "vehiclYachtsBoatsAircrafts": 0, # Not provided by Fi MCP
        "archCollDrawPaintSulpArt": 0 # Not provided by Fi MCP
    }

    if net_worth_data.get("assetValues"):
        for asset in net_worth_data["assetValues"]:
            value = convert_fi_currency_to_inr_int(asset.get("totalValue"))
            if asset["assetType"] == "ASSET_TYPE_SAVINGS_ACCOUNTS":
                itr_prefill_data["scheduleAL"]["movableAsset"]["depositsInBank"] = value
            elif asset["assetType"] in ["ASSET_TYPE_MUTUAL_FUND", "ASSET_TYPE_INDIAN_SECURITIES", "ASSET_TYPE_US_SECURITIES"]:
                # Aggregate all securities into one field for AL
                itr_prefill_data["scheduleAL"]["movableAsset"]["sharesAndSecurities"] += value
            # EPF already mapped to form3CD longTermInv.others

    if net_worth_data.get("liabilityValues"):
        total_liabilities = 0
        for liability in net_worth_data["liabilityValues"]:
            total_liabilities += convert_fi_currency_to_inr_int(liability.get("totalValue"))

        # Map total liabilities to a general unsecured loan or other payable in form3CD
        # This is a very simplified mapping for liabilities on the balance sheet
        itr_prefill_data.setdefault("form3CD", {}).setdefault("partABS", {}).setdefault("fundSrc", {}).setdefault("loanFunds", {}).setdefault("unsecrLoan", {})["frmOthrs"] = total_liabilities
    
    # Fi MCP provides high-level asset/liability. More granular Schedule AL fields
    # like specific immovable properties, vehicles, jewellery acquisition costs/dates are missing.
    warnings.append("Detailed asset and liability breakdown for Schedule AL may be incomplete. Please review and manually add immovable property, vehicles, and other specific assets/liabilities if applicable.")

    # --- 9. Populate Credit Report based fields (e.g., loans from FIs for deductions, if applicable) ---
    if credit_report_data and credit_report_data[0].get("creditReportData"):
        # For deductions like 80EE/EEA/EEB (interest on housing/EV loans), or 43B (interest payable to FIs)
        # This requires more advanced logic to determine if a loan qualifies for specific deductions.
        # We can sum up total outstanding loans as a general liability indicator in a balance sheet (if ITR3/4).
        for acc in credit_report_data[0]["creditReportData"].get("creditAccount", {}).get("creditAccountDetails", []):
            loan_balance = convert_fi_currency_to_inr_int(acc.get("currentBalance"))
            # Example for interest deduction, if it were directly available and categorizable
            # For 43B, need to know if payment is due but not paid
            # itr_prefill_data.setdefault("form3CD", {}).setdefault("partAOI", {}).setdefault("amtDisall43B", {}).setdefault("amtUs43B", {})["intPayaleToFINBFC"] = some_interest_amt
            pass # No direct mapping for specific tax deductions from this level of credit data.
    else:
        warnings.append("Credit report data not available, so no pre-fill for loan-related deductions.")


    # --- 10. Populate form3CD.partAPL (Profit and Loss) & Business Income (Placeholders) ---
    # Fi MCP primarily focuses on personal financial health, not detailed business P&L.
    # Therefore, most P&L fields for ITR3/4 will be zero or require manual input.
    itr_prefill_data.setdefault("form3CD", {})["partAPL"] = {
        "creditsToPL": {"othIncome": {"dividends": 0, "interestInc": 0, "otherIncDtls": []}}, # Can be populated from 26AS data
        "debitsToPL": {"employeeComp": {"salsWages": 0}, "depreciationAmort": 0}, # Placeholders
        "grossProfit": 0,
        "netIncomeFrmSpecActivity": 0,
        "turnverFrmSpecActivity": 0,
        "persumptiveInc44AD": {"totPersumptiveInc44AD": 0},
        "persumptiveInc44ADA": {"totPersumptiveInc44ADA": 0},
    }
    warnings.append("Business/Profession income and detailed Profit & Loss A/c cannot be pre-filled from Fi MCP. Please enter manually if applicable.")
    warnings.append("Presumptive income under 44AD/ADA/AE cannot be determined by Fi MCP. Please enter manually if applicable.")


    # --- 11. Final Return Structure ---
    final_itr_json = {
        "$schema": "https://json-schema.org/draft/2019-09/schema",
        "personalInfo": itr_prefill_data["personalInfo"],
        "filingStatus": itr_prefill_data["filingStatus"],
        "bankAccountDtls": itr_prefill_data["bankAccountDtls"],
        "insights": itr_prefill_data["insights"],
        "form26as": itr_prefill_data["form26as"], # Contains some aggregated TDS/Tax from 26AS
        "scheduleAL": itr_prefill_data["scheduleAL"],
        "form3CD": itr_prefill_data["form3CD"],
        "ais": itr_prefill_data.get("ais", {}), # Contains 112A from AIS
        "verification": {
            "declaration": {
                "assesseeVerName": f"{itr_prefill_data['personalInfo']['assesseeName'].get('firstName', '')} {itr_prefill_data['personalInfo']['assesseeName'].get('surNameOrOrgName', '')}".strip(),
                "assesseeVerPAN": pan,
                "fatherName": "Father's Name Placeholder" # Default, not in Fi MCP
            },
            "capacity": "Self", # Default, could be 'Representative' if applicable
            "repIsPresent": False
        },
        "warnings": warnings,
        "errors": errors
    }

    # Clean up empty dictionaries and lists for cleaner JSON output
    def clean_empty_structures(d):
        if not isinstance(d, (dict, list)):
            return d
        if isinstance(d, list):
            return [clean_empty_structures(v) for v in d if v is not None and v != {} and v != []]
        return {k: clean_empty_structures(v) for k, v in d.items() if v is not None and v != {} and v != []}

    final_itr_json = clean_empty_structures(final_itr_json)

    return final_itr_json