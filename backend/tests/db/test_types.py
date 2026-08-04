from datetime import UTC, datetime, timedelta, timezone

import pytest
from sqlalchemy.dialects import postgresql

from app.db.types import UTCDateTime


def test_utc_datetime_normalizes_aware_values() -> None:
    value = datetime(2026, 8, 4, 12, 30, tzinfo=timezone(timedelta(hours=8)))

    dialect = postgresql.dialect()  # type: ignore[no-untyped-call]
    normalized = UTCDateTime().process_bind_param(value, dialect)

    assert normalized == datetime(2026, 8, 4, 4, 30, tzinfo=UTC)


def test_utc_datetime_rejects_naive_values() -> None:
    value = datetime(2026, 8, 4, 12, 30)  # noqa: DTZ001
    dialect = postgresql.dialect()  # type: ignore[no-untyped-call]

    with pytest.raises(ValueError, match="timezone information"):
        UTCDateTime().process_bind_param(value, dialect)
