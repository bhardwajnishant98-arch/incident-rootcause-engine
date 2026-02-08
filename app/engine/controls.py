"""Control gap detection based on keyword signals."""

from __future__ import annotations

from typing import Any, Dict, List

RECOMMENDATIONS_BY_CATEGORY = {
    "Process": [
        "Require peer-reviewed change approvals.",
        "Introduce automated rollback checks.",
    ],
    "Technology": [
        "Add proactive capacity alerts.",
        "Improve automated failover coverage.",
    ],
    "Security": [
        "Enforce least-privilege access reviews.",
        "Rotate sensitive credentials on a schedule.",
    ],
    "External": [
        "Add vendor redundancy or fallback providers.",
        "Negotiate stronger SLAs with third parties.",
    ],
}

DEFAULT_RECOMMENDATIONS = [
    "Improve monitoring and alert coverage.",
    "Review operational runbooks and response drills.",
    "Perform post-incident retrospectives with owners.",
]


def analyze_controls(incident: Dict[str, Any], controls: List[Dict[str, Any]]) -> Dict[str, Any]:
    description = f"{incident.get('title', '')} {incident.get('description', '')}".lower()
    matched_controls: List[Dict[str, Any]] = []

    for control in controls:
        signals = [signal.lower() for signal in control.get("signals", [])]
        if any(signal in description for signal in signals):
            matched_controls.append(control)

    matched_controls = matched_controls[:5]

    recommendations: List[str] = []
    for control in matched_controls:
        category = control.get("category")
        recommendations.extend(RECOMMENDATIONS_BY_CATEGORY.get(category, []))

    if not recommendations:
        recommendations = DEFAULT_RECOMMENDATIONS.copy()

    recommendations = list(dict.fromkeys(recommendations))[:6]

    return {
        "matched_controls": matched_controls,
        "recommendations": recommendations,
    }
