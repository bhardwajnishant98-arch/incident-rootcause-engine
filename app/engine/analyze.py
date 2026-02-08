"""Incident analysis orchestration."""

from __future__ import annotations

from typing import Any, Dict

from app.engine.classify import classify_incident
from app.engine.controls import analyze_controls
from app.engine.rca import analyze_rca


def _build_exec_summary(incident: Dict[str, Any], classification: Dict[str, Any]) -> list[str]:
    return [
        f"Classification: {classification['classification']} ({classification['severity']}).",
        f"Score: {classification['score']} based on impact signals.",
        f"Service: {incident.get('service_name', 'unknown')}.",
        f"Customer impact: {incident.get('customer_impact', 'none')}.",
        f"Data involved: {incident.get('data_involved', 'none')}.",
    ]


def analyze_incident(
    incident: Dict[str, Any], taxonomy: Dict[str, Any], controls: list[Dict[str, Any]]
) -> Dict[str, Any]:
    classification = classify_incident(incident, taxonomy)
    rca = analyze_rca(incident)
    control_analysis = analyze_controls(incident, controls)

    executive_summary = _build_exec_summary(incident, classification)

    return {
        "title": incident.get("title", "Untitled incident"),
        "description": incident.get("description", ""),
        "service_name": incident.get("service_name", ""),
        "customer_impact": incident.get("customer_impact", "none"),
        "data_involved": incident.get("data_involved", "none"),
        "regulatory_relevance": incident.get("regulatory_relevance", "none"),
        "financial_loss_gbp": incident.get("financial_loss_gbp", 0),
        "classification": classification,
        "rca": rca,
        "controls": control_analysis,
        "executive_summary": executive_summary,
    }
