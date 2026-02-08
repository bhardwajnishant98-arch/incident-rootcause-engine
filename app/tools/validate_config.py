"""Validate config JSON files."""

import json
from pathlib import Path


def main() -> None:
    taxonomy_path = Path("data/taxonomy.json")
    controls_path = Path("data/controls_library.json")

    with taxonomy_path.open("r", encoding="utf-8") as handle:
        json.load(handle)

    with controls_path.open("r", encoding="utf-8") as handle:
        json.load(handle)

    print("CONFIG OK")


if __name__ == "__main__":
    main()
