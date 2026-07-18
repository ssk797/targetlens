from app.services.scoring.rules import (
    EVIDENCE_WEIGHTS,
    OPPORTUNITY_WEIGHTS,
    RISK_WEIGHTS,
    apply_redline_caps,
    clamp,
    recommendation_for_score,
    weighted_score,
)
from app.services.scoring.schemas import ScoreRequest, ScoreResult


def calculate_score(request: ScoreRequest) -> ScoreResult:
    """Calculate the auditable three-axis score on the server.

    Model output may propose the input dimensions, but this function is the
    only place that computes the final score and applies redline caps.
    """

    base_opportunity = weighted_score(request.opportunity.model_dump(), OPPORTUNITY_WEIGHTS)
    risk_burden = weighted_score(request.risk.model_dump(), RISK_WEIGHTS)
    evidence_confidence = weighted_score(request.evidence.model_dump(), EVIDENCE_WEIGHTS)

    confidence_factor = 0.65 + 0.35 * evidence_confidence / 100
    risk_penalty = max(0, risk_burden - 50) * 0.30
    adjusted_score = clamp(base_opportunity * confidence_factor - risk_penalty)
    raw_recommendation = recommendation_for_score(adjusted_score)
    recommendation = apply_redline_caps(raw_recommendation, request.redlines)

    return ScoreResult(
        base_opportunity=round(base_opportunity, 2),
        risk_burden=round(risk_burden, 2),
        evidence_confidence=round(evidence_confidence, 2),
        confidence_factor=round(confidence_factor, 4),
        risk_penalty=round(risk_penalty, 2),
        adjusted_score=round(adjusted_score, 2),
        recommendation=recommendation,
        manual_review_required=any(r.triggered and r.requires_human_review for r in request.redlines),
        redlines=request.redlines,
        breakdown={
            "opportunity": round(base_opportunity, 2),
            "risk": round(risk_burden, 2),
            "evidence": round(evidence_confidence, 2),
            "raw_recommendation": raw_recommendation,
        },
    )
