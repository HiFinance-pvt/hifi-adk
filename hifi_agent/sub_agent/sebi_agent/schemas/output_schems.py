from pydantic import BaseModel, Field
from typing import List, Literal


class PotentialAnomaly(BaseModel):
    description: str = Field(..., description="Description of the anomaly detected")
    severity: Literal["low", "medium", "high"] = Field(..., description="Severity level of the anomaly")
    related_regulation: str = Field(..., description="SEBI regulation or guideline related to this anomaly")
    recommended_action: str = Field(..., description="Recommended action for the user to resolve the issue")


class SEBIAnalysisOutput(BaseModel):
    summary: str = Field(..., description="Brief summary of the overall analysis")
    potential_anomalies: List[PotentialAnomaly] = Field(default_factory=list, description="List of detected anomalies")
    compliance_score: int = Field(..., ge=0, le=100, description="Score out of 100 indicating SEBI compliance level")
    alert_flag: bool = Field(..., description="Whether a significant compliance issue or fraud alert was raised")
