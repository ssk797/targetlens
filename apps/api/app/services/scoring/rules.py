from collections.abc import Mapping

from app.services.scoring.schemas import Recommendation, RedlineInput


OPPORTUNITY_WEIGHTS: Mapping[str, float] = {
    "unmet_need": 15,
    "target_validation": 20,
    "patient_selection": 15,
    "modality_fit": 15,
    "differentiation_space": 15,
    "clinical_feasibility": 10,
    "safety_controllability": 10,
}

RISK_WEIGHTS: Mapping[str, float] = {
    "normal_tissue_window": 20,
    "known_safety_class_risk": 20,
    "clinical_failure_risk": 20,
    "regulatory_risk": 15,
    "scientific_uncertainty": 15,
    "competitive_window": 10,
}

EVIDENCE_WEIGHTS: Mapping[str, float] = {
    "evidence_coverage": 30,
    "source_authority": 25,
    "cross_source_consistency": 20,
    "freshness": 15,
    "scope_clarity": 10,
}

RECOMMENDATION_RANK: Mapping[Recommendation, int] = {
    "STOP": 0,
    "HOLD": 1,
    "PILOT": 2,
    "GO": 3,
}


def clamp(value: float, lower: float = 0, upper: float = 100) -> float:
    return min(upper, max(lower, value))


def weighted_score(values: Mapping[str, float], weights: Mapping[str, float]) -> float:
    missing = set(weights) - set(values)
    if missing:
        raise ValueError(f"missing scoring dimensions: {', '.join(sorted(missing))}")
    total_weight = sum(weights.values())
    return sum(values[name] * weight for name, weight in weights.items()) / total_weight


def recommendation_for_score(adjusted_score: float) -> Recommendation:
    if adjusted_score >= 75:
        return "GO"
    if adjusted_score >= 55:
        return "PILOT"
    if adjusted_score >= 35:
        return "HOLD"
    return "STOP"


def apply_redline_caps(recommendation: Recommendation, redlines: list[RedlineInput]) -> Recommendation:
    triggered_caps = [redline.recommendation_cap for redline in redlines if redline.triggered]
    if not triggered_caps:
        return recommendation
    return min(
        [recommendation, *triggered_caps],
        key=lambda option: RECOMMENDATION_RANK[option],
    )
