"""Classification and severity scoring for incidents."""

from __future__ import annotations

from typing import Any, Dict, List


def _bucket_outage_minutes(minutes: float) -> str:
    if minutes <= 0:
        return "none"
    if minutes <= 15:
        return "short"
    if minutes <= 60:
        return "moderate"
    return "long"


def _bucket_users_impacted(percent: float) -> str:
    if percent <= 0:
        return "none"
    if percent <= 10:
        return "small"
    if percent <= 40:
        return "moderate"
    return "large"


def _bucket_financial_loss(loss_gbp: float) -> str:
    if loss_gbp <= 0:
        return "none"
    if loss_gbp <= 5000:
        return "low"
    if loss_gbp <= 25000:
        return "medium"
    return "high"


def classify_incident(incident: Dict[str, Any], taxonomy: Dict[str, Any]) -> Dict[str, Any]:
    scoring = taxonomy.get("scoring", {})
    score_breakdown: Dict[str, Dict[str, Any]] = {}
    assumptions: List[str] = []

    customer_impact = incident.get("customer_impact", "none")
    outage_minutes = float(incident.get("outage_minutes", 0) or 0)
    users_impacted_percent = float(incident.get("users_impacted_percent", 0) or 0)
    data_involved = incident.get("data_involved", "none")
    regulatory_relevance = incident.get("regulatory_relevance", "none")
    financial_loss_gbp = float(incident.get("financial_loss_gbp", 0) or 0)

    outage_bucket = _bucket_outage_minutes(outage_minutes)
    users_bucket = _bucket_users_impacted(users_impacted_percent)
    loss_bucket = _bucket_financial_loss(financial_loss_gbp)

    score_breakdown["customer_impact"] = {
        "bucket": customer_impact,
        "score": scoring.get("customer_impact", {}).get(customer_impact, 0),
    }
    score_breakdown["outage_minutes"] = {
        "bucket": outage_bucket,
        "score": scoring.get("outage_minutes", {}).get(outage_bucket, 0),
    }
    score_breakdown["users_impacted_percent"] = {
        "bucket": users_bucket,
        "score": scoring.get("users_impacted_percent", {}).get(users_bucket, 0),
    }
    score_breakdown["data_involved"] = {
        "bucket": data_involved,
        "score": scoring.get("data_involved", {}).get(data_involved, 0),
    }
    score_breakdown["regulatory_relevance"] = {
        "bucket": regulatory_relevance,
        "score": scoring.get("regulatory_relevance", {}).get(regulatory_relevance, 0),
    }
    score_breakdown["financial_loss_gbp"] = {
        "bucket": loss_bucket,
        "score": scoring.get("financial_loss_gbp", {}).get(loss_bucket, 0),
    }

    score = sum(item["score"] for item in score_breakdown.values())

    severity = "SEV4"
    for threshold in taxonomy.get("severity_thresholds", []):
        if score >= threshold.get("min_score", 0):
            severity = threshold.get("label", severity)
            break

    detected_before_impact = bool(incident.get("detected_before_impact", False))
    if detected_before_impact and (
        data_involved != "none" or regulatory_relevance in {"medium", "high"}
    ):
        classification = "NEAR_MISS"
        assumptions.append("Detected before impact with sensitive or regulated data present.")
    elif outage_minutes > 0 or customer_impact != "none" or data_involved in {
        "pii",
        "financial",
        "credentials",
    }:
        classification = "INCIDENT"
        assumptions.append("Impact indicators exceeded issue thresholds.")
    else:
        classification = "ISSUE"
        assumptions.append("No outage or customer impact detected.")

    return {
        "score": score,
        "severity": severity,
        "classification": classification,
        "score_breakdown": score_breakdown,
        "assumptions": assumptions,
    }
