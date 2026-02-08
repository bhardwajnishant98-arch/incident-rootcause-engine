"""Root cause analysis heuristics."""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

KEYWORDS = {
    "TECHNOLOGY": {
        "signals": ["502", "timeout", "latency", "disk", "config", "error", "500"],
        "subcategory": "Reliability or configuration",
    },
    "PROCESS": {
        "signals": ["deploy", "change", "approval", "testing", "runbook", "rollback"],
        "subcategory": "Change management",
    },
    "PEOPLE": {
        "signals": ["manual", "mistake", "onboarding", "handoff", "training"],
        "subcategory": "Human process",
    },
    "EXTERNAL": {
        "signals": ["vendor", "cloud", "provider", "outage", "third-party"],
        "subcategory": "Third-party dependency",
    },
}

CONTRIBUTING_CANDIDATES = {
    "Monitoring gap": ["monitor", "alert", "detect"],
    "Capacity planning": ["capacity", "traffic", "load"],
    "Documentation gap": ["runbook", "handoff", "knowledge"],
    "Resilience gap": ["failover", "redundant", "backup"],
}


def _find_matches(text: str, signals: List[str]) -> List[str]:
    return [signal for signal in signals if signal in text]


def analyze_rca(incident: Dict[str, Any]) -> Dict[str, Any]:
    description = f"{incident.get('title', '')} {incident.get('description', '')}".lower()

    category_scores: List[Tuple[str, int]] = []
    evidence: List[str] = []
    for category, details in KEYWORDS.items():
        matches = _find_matches(description, details["signals"])
        if matches:
            category_scores.append((category, len(matches)))
            evidence.extend([f"Matched '{match}' for {category}." for match in matches])

    if category_scores:
        category_scores.sort(key=lambda item: item[1], reverse=True)
        primary_category = category_scores[0][0]
    else:
        primary_category = "TECHNOLOGY"
        evidence.append("Defaulted to technology RCA due to no keyword matches.")

    primary_subcategory = KEYWORDS.get(primary_category, {}).get("subcategory", "General")

    contributing: List[Dict[str, str]] = []
    for label, signals in CONTRIBUTING_CANDIDATES.items():
        if _find_matches(description, signals):
            contributing.append({"category": label, "subcategory": label})
    contributing = contributing[:4]

    total_hits = sum(score for _, score in category_scores) or 1
    confidence = min(0.9, 0.4 + (total_hits * 0.1))

    return {
        "primary": {
            "category": primary_category,
            "subcategory": primary_subcategory,
        },
        "contributing": contributing,
        "confidence": round(confidence, 2),
        "evidence": evidence,
    }
