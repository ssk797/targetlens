from app.services.scoring.engine import calculate_score
from app.services.scoring.schemas import EvidenceDimensions, OpportunityDimensions, RedlineInput, RiskDimensions, ScoreRequest


def request_with(value: float = 100, risk: float = 0, evidence: float = 100, redlines: list[RedlineInput] | None = None) -> ScoreRequest:
    return ScoreRequest(
        opportunity=OpportunityDimensions(**{field: value for field in OpportunityDimensions.model_fields}),
        risk=RiskDimensions(**{field: risk for field in RiskDimensions.model_fields}),
        evidence=EvidenceDimensions(**{field: evidence for field in EvidenceDimensions.model_fields}),
        redlines=redlines or [],
    )


def test_formula_keeps_perfect_opportunity_at_100() -> None:
    result = calculate_score(request_with())

    assert result.base_opportunity == 100
    assert result.risk_burden == 0
    assert result.evidence_confidence == 100
    assert result.confidence_factor == 1
    assert result.adjusted_score == 100
    assert result.recommendation == "GO"


def test_risk_penalty_and_confidence_factor_are_applied() -> None:
    result = calculate_score(request_with(value=80, risk=100, evidence=0))

    assert result.confidence_factor == 0.65
    assert result.risk_penalty == 15
    assert result.adjusted_score == 37
    assert result.recommendation == "HOLD"


def test_triggered_redline_caps_recommendation_and_requires_review() -> None:
    redline = RedlineInput(
        id="redline-1",
        name="不可忽略的安全信号",
        triggered=True,
        rationale="需要人工复核",
        evidence_ids=["evidence-1"],
        recommendation_cap="PILOT",
    )

    result = calculate_score(request_with(redlines=[redline]))

    assert result.recommendation == "PILOT"
    assert result.manual_review_required is True
    assert result.redlines[0].evidence_ids == ["evidence-1"]
