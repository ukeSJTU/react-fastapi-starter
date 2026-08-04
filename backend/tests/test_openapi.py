import json
from pathlib import Path
from typing import Any, cast

from app.main import create_app
from app.scripts.export_openapi import export_openapi
from tests.factories import build_settings


def operation_ids(schema: dict[str, Any]) -> list[str]:
    identifiers: list[str] = []
    paths = cast(dict[str, dict[str, dict[str, Any]]], schema["paths"])
    for path_item in paths.values():
        for operation in path_item.values():
            identifier = operation.get("operationId")
            if identifier is not None:
                identifiers.append(cast(str, identifier))
    return identifiers


def test_openapi_operation_ids_are_stable_and_unique() -> None:
    schema = create_app(build_settings()).openapi()
    identifiers = operation_ids(schema)

    assert identifiers == ["getHealth"]
    assert len(identifiers) == len(set(identifiers))


def test_openapi_can_be_exported_without_http_server(tmp_path: Path) -> None:
    output = tmp_path / "nested" / "openapi.json"

    export_openapi(create_app(build_settings()), output)

    schema = json.loads(output.read_text(encoding="utf-8"))
    assert schema["info"]["title"] == "Backend API"
    assert operation_ids(schema) == ["getHealth"]
