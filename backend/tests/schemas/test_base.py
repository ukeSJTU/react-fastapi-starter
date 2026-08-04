from datetime import UTC, datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from app.schemas.base import BaseSchema, UTCDateTime


class TimestampedSchema(BaseSchema):
    created_at: UTCDateTime


def test_schema_uses_camel_case_and_serializes_utc_with_z() -> None:
    model = TimestampedSchema(
        created_at=datetime(2026, 8, 4, 12, 30, tzinfo=timezone(timedelta(hours=8)))
    )

    assert model.model_dump(mode="json") == {"createdAt": "2026-08-04T04:30:00Z"}


def test_schema_accepts_camel_case_input() -> None:
    model = TimestampedSchema.model_validate({"createdAt": "2026-08-04T04:30:00Z"})

    assert model.created_at == datetime(2026, 8, 4, 4, 30, tzinfo=UTC)


def test_schema_rejects_naive_datetime() -> None:
    with pytest.raises(ValidationError, match="timezone information"):
        TimestampedSchema(
            created_at=datetime(2026, 8, 4, 12, 30)  # noqa: DTZ001
        )
