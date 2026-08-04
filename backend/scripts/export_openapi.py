import json
from pathlib import Path
from typing import Any

from app.main import app

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
OPENAPI_PATH = REPOSITORY_ROOT / "openapi.json"


def export_openapi() -> None:
    schema: dict[str, Any] = app.openapi()
    OPENAPI_PATH.write_text(
        json.dumps(schema, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    export_openapi()
