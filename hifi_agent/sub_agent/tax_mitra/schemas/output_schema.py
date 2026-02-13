from typing import Optional, Union, Literal
from pydantic import BaseModel, Field


class QuestionOption(BaseModel):
    """Represents a single question with rich UI options"""
    title: str = Field(..., description="The question text to display")
    description: Optional[str] = Field(None, description="Additional context or help text for the question")
    type: Literal["text", "number", "select", "multiselect", "date", "email", "tel", "file"] = Field(
        ..., 
        description="The input type for the question"
    )
    options: Optional[list[str]] = Field(None, description="Available options for select/multiselect types")
    required: bool = Field(True, description="Whether this question must be answered")
    default: Optional[str] = Field(None, description="Default value for the field")
    placeholder: Optional[str] = Field(None, description="Placeholder text for the input")
    value: Optional[str] = Field(None, description="Pre-filled value if available")
    error: Optional[str] = Field(None, description="Error message to display")
    min: Optional[float] = Field(None, description="Minimum value for number inputs")
    max: Optional[float] = Field(None, description="Maximum value for number inputs")


class TaxMitraResponse(BaseModel):
    """Structured response format for Tax Mitra agent"""
    message: str = Field(..., description="The main response message to display to the user")
    questions: Optional[Union[list[str], list[QuestionOption]]] = Field(
        None, 
        description="Questions to ask the user - can be simple strings or rich question objects"
    )
    data: Optional[dict] = Field(None, description="Any additional data or results to display")
    status: Optional[Literal["success", "error", "pending", "info"]] = Field(
        "info", 
        description="Status of the response"
    )
    action: Optional[Literal["input_required", "processing", "completed", "error"]] = Field(
        None, 
        description="What action is expected next"
    )
    progress: Optional[dict] = Field(
        None, 
        description="Progress information with keys like 'current_step', 'total_steps', 'step_name'"
    )


# Example usage schemas for different scenarios
class TaxCalculationResult(BaseModel):
    """Result of tax calculation"""
    gross_income: float
    taxable_income: float
    total_tax: float
    tax_regime: str
    breakdown: dict


class ITRSubmissionResult(BaseModel):
    """Result of ITR form submission"""
    acknowledgement_number: str
    submission_date: str
    itr_form_type: str
    status: str
    message: str


class RefundTrackingResult(BaseModel):
    """Result of refund tracking"""
    acknowledgement_number: str
    refund_amount: Optional[float]
    refund_status: str
    expected_date: Optional[str]
    remarks: Optional[str]
