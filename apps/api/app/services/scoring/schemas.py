from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


ScoreValue = Annotated[float, Field(ge=0, le=100)]


class OpportunityDimensions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    unmet_need: ScoreValue
    target_validation: ScoreValue
    patient_selection: ScoreValue
    modality_fit: ScoreValue
    differentiation_space: ScoreValue
    clinical_feasibility: ScoreValue
    safety_controllability: ScoreValue


class RiskDimensions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    normal_tissue_window: ScoreValue
    known_safety_class_risk: ScoreValue
    clinical_failure_risk: ScoreValue
    regulatory_risk: ScoreValue
    scientific_uncertainty: ScoreValue
    competitive_window: ScoreValue


class EvidenceDimensions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_coverage: ScoreValue
    source_authority: ScoreValue
    cross_source_consistency: ScoreValue
    freshness: ScoreValue
    scope_clarity: ScoreValue


Recommendation = Literal["GO", "PILOT", "HOLD", "STOP"]


class RedlineInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1, max_length=120)
    name: str = Field(min_length=1, max_length=200)
    triggered: bool
    rationale: str = Field(default="", max_length=1000)
    evidence_ids: list[str] = Field(default_factory=list)
    mitigable: bool = True
    requires_human_review: bool = True
    recommendation_cap: Recommendation = "HOLD"


class ScoreRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    opportunity: OpportunityDimensions
    risk: RiskDimensions
    evidence: EvidenceDimensions
    redlines: list[RedlineInput] = Field(default_factory=list)


class ScoreResult(BaseModel):
    base_opportunity: float
    risk_burden: float
    evidence_confidence: float
    confidence_factor: float
    risk_penalty: float
    adjusted_score: float
    recommendation: Recommendation
    manual_review_required: bool
    redlines: list[RedlineInput]
    breakdown: dict[str, float | str]
