# Incident Root Cause Analysis Engine

A Python project for building an incident root cause analysis engine using the standard library.

## Setup

No external dependencies are required.

## Run

Validate configs:

```bash
python app/tools/validate_config.py
```

Run analysis on sample incidents:

```bash
python -m app.cli --input data/examples.jsonl --outdir outputs
```

## Tests

```bash
python -m unittest
```
