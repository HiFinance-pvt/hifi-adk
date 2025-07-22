# This code is the updated 'tool' function.
# It will send data to an external HTTP server (your mock_server.py).

from typing import Dict, Any
import json
import requests # Import the requests library
from datetime import datetime
from google.adk.tools.tool_context import ToolContext
from .generate_itr_prefill_json import generate_itr_prefill_json
from .shared_utils import validate_pan
import os
from dotenv import load_dotenv
load_dotenv()

async def fill_and_submit_itr_form(itr_form_type: str, pan: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Prepare and submit Income Tax Return (ITR) form by sending data to an external API server.
    
    Args:
        itr_form_type (str): Type of ITR form (ITR1, ITR2, ITR3, ITR4)
        pan (str): User's Permanent Account Number

    It generates prefill json
    Returns:
        dict: Submission result from the external API, containing:
            - acknowledgement_number: ITR-V acknowledgement number
            - submission_status: Success/failure status
            - submission_date: Date and time of submission
            - verification_required: Whether e-verification is needed
            - errors: Any validation errors encountered
    """
    
    # Validate PAN using shared utility
    if not validate_pan(pan):
        raise ValueError("Invalid PAN format")
    
    MOCK_SERVER_URL = os.getenv("ITR_SERVER_URL")

    if MOCK_SERVER_URL is None:
        raise ValueError("ITR_SERVER_URL is not set in the environment variables")
    
    if MOCK_SERVER_URL == "":
        raise ValueError("ITR_SERVER_URL is empty in the environment variables")

    user_data = await generate_itr_prefill_json(pan, "2025-26", tool_context)

    # Prepare the payload to send to the mock server
    payload = {
        "itr_form_type": itr_form_type,
        "user_data": user_data,
        "pan": pan
    }

    try:
        # Send a POST request to your mock server
        # The timeout helps prevent the request from hanging indefinitely
        response = requests.post(MOCK_SERVER_URL, json=payload, timeout=10)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

        # Parse the JSON response from the mock server
        submission_result = response.json()
        
        return submission_result

    except requests.exceptions.ConnectionError as e:
        return {
            'acknowledgement_number': None,
            'submission_status': 'failed',
            'submission_date': datetime.now().isoformat(),
            'verification_required': False,
            'errors': [f"Connection to mock server failed: {str(e)}. Please ensure your mock_server.py is running on {MOCK_SERVER_URL}"],
            'warnings': []
        }
    except requests.exceptions.Timeout:
        return {
            'acknowledgement_number': None,
            'submission_status': 'failed',
            'submission_date': datetime.now().isoformat(),
            'verification_required': False,
            'errors': [f"Request to mock server timed out after 10 seconds. Is the server busy or not running?"],
            'warnings': []
        }
    except requests.exceptions.RequestException as e:
        # Catch any other requests-related errors (e.g., HTTP errors, invalid JSON response)
        try:
            error_response = response.json()
            errors = error_response.get("errors", [f"HTTP Error from mock server: {response.status_code} - {error_response.get('error', 'Unknown Error')}"])
            return {
                'acknowledgement_number': None,
                'submission_status': 'failed',
                'submission_date': datetime.now().isoformat(),
                'verification_required': False,
                'errors': errors,
                'warnings': error_response.get("warnings", [])
            }
        except json.JSONDecodeError:
            # If response is not JSON
            return {
                'acknowledgement_number': None,
                'submission_status': 'failed',
                'submission_date': datetime.now().isoformat(),
                'verification_required': False,
                'errors': [f"Request to mock server failed with status {response.status_code} and non-JSON response: {response.text}"],
                'warnings': []
            }
    except Exception as e:
        # Catch any other unexpected errors
        return {
            'acknowledgement_number': None,
            'submission_status': 'failed',
            'submission_date': datetime.now().isoformat(),
            'verification_required': False,
            'errors': [f"An unexpected error occurred during submission: {str(e)}"],
            'warnings': []
        }