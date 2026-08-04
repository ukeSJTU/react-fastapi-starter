import argparse
import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI

from app.main import app as default_app


def export_openapi(app: FastAPI, output: Path) -> None:
    schema: dict[str, Any] = app.openapi()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(schema, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export the application OpenAPI schema"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("openapi.json"),
        help="Destination path (default: openapi.json)",
    )
    arguments = parser.parse_args()
    export_openapi(default_app, arguments.output)


if __name__ == "__main__":
    main()
