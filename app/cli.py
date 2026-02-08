"""CLI runner for incident analysis."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from app.engine.analyze import analyze_incident


CSV_COLUMNS = [
    "timestamp_utc",
    "title",
    "classification",
    "severity",
    "score",
    "service_name",
    "primary_rca_category",
    "primary_rca_subcategory",
    "top_control_gap",
    "customer_impact",
    "data_involved",
    "regulatory_relevance",
    "financial_loss_gbp",
    "confidence",
    "exec_summary_short",
]

SEVERITY_MAP = {
    "SEV1": "Critical",
    "SEV2": "High",
    "SEV3": "Medium",
    "SEV4": "Low",
}


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _load_incidents_from_jsonl(path: Path) -> List[Dict[str, Any]]:
    incidents = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            incidents.append(json.loads(line))
    return incidents


def _write_report(analyses: List[Dict[str, Any]], report_path: Path) -> None:
    lines: List[str] = ["# Incident RCA Report", ""]
    for analysis in analyses:
        lines.append(f"## {analysis['title']}")
        lines.append("")
        lines.append("### Executive Summary")
        for bullet in analysis.get("executive_summary", []):
            lines.append(f"- {bullet}")
        lines.append("")
        lines.append("### Root Cause Analysis")
        primary = analysis.get("rca", {}).get("primary", {})
        lines.append(f"Primary: {primary.get('category', '')} - {primary.get('subcategory', '')}")
        lines.append("")
        lines.append("### Controls")
        controls = analysis.get("controls", {}).get("matched_controls", [])
        if controls:
            lines.append("Matched Controls:")
            for control in controls:
                lines.append(f"- {control.get('name', '')}")
        else:
            lines.append("Matched Controls: None")
        lines.append("")
        lines.append("Recommendations:")
        for rec in analysis.get("controls", {}).get("recommendations", []):
            lines.append(f"- {rec}")
        lines.append("")
    report_path.write_text("\n".join(lines), encoding="utf-8")


def _write_csv(analyses: List[Dict[str, Any]], csv_path: Path) -> None:
    timestamp = datetime.now(timezone.utc).isoformat()
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for analysis in analyses:
            classification = analysis.get("classification", {})
            rca = analysis.get("rca", {})
            controls = analysis.get("controls", {})
            exec_summary = " ".join(analysis.get("executive_summary", []))
            exec_summary_short = exec_summary[:140]

            top_control_gap = ""
            matched_controls = controls.get("matched_controls", [])
            if matched_controls:
                top_control_gap = matched_controls[0].get("name", "")

            severity = classification.get("severity", "SEV4")
            row = {
                "timestamp_utc": timestamp,
                "title": analysis.get("title", ""),
                "classification": classification.get("classification", ""),
                "severity": SEVERITY_MAP.get(severity, "Low"),
                "score": classification.get("score", 0),
                "service_name": analysis.get("service_name", ""),
                "primary_rca_category": rca.get("primary", {}).get("category", ""),
                "primary_rca_subcategory": rca.get("primary", {}).get("subcategory", ""),
                "top_control_gap": top_control_gap,
                "customer_impact": analysis.get("customer_impact", ""),
                "data_involved": analysis.get("data_involved", ""),
                "regulatory_relevance": analysis.get("regulatory_relevance", ""),
                "financial_loss_gbp": analysis.get("financial_loss_gbp", 0),
                "confidence": rca.get("confidence", 0),
                "exec_summary_short": exec_summary_short,
            }
            writer.writerow(row)


def _write_outputs(analyses: List[Dict[str, Any]], outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    analysis_path = outdir / "analysis.json"
    report_path = outdir / "report.md"
    csv_path = outdir / "risk_register.csv"

    analysis_path.write_text(json.dumps(analyses, indent=2), encoding="utf-8")
    _write_report(analyses, report_path)
    _write_csv(analyses, csv_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Incident RCA engine CLI")
    parser.add_argument("--input", help="Path to JSONL incidents")
    parser.add_argument("--title", help="Incident title")
    parser.add_argument("--description", help="Incident description")
    parser.add_argument("--outdir", required=True, help="Output directory")
    args = parser.parse_args()

    taxonomy = _load_json(Path("data/taxonomy.json"))
    controls = _load_json(Path("data/controls_library.json"))

    incidents: List[Dict[str, Any]] = []
    if args.input:
        incidents = _load_incidents_from_jsonl(Path(args.input))
    elif args.title and args.description:
        incidents = [
            {
                "title": args.title,
                "description": args.description,
                "customer_impact": "none",
                "outage_minutes": 0,
                "users_impacted_percent": 0,
                "data_involved": "none",
                "regulatory_relevance": "none",
                "financial_loss_gbp": 0,
                "detected_before_impact": False,
            }
        ]
    else:
        raise SystemExit("Provide --input or both --title and --description")

    analyses = [analyze_incident(incident, taxonomy, controls) for incident in incidents]
    _write_outputs(analyses, Path(args.outdir))


if __name__ == "__main__":
    main()
