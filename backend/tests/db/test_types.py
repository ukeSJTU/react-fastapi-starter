from datetime import UTC, datetime, timedelta, timezone

import pytest
from sqlalchemy import Column, MetaData, Table, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.types import UTCDateTime, as_utc


def test_as_utc_normalizes_aware_values() -> None:
    value = datetime(2026, 8, 4, 12, 30, tzinfo=timezone(timedelta(hours=8)))

    assert as_utc(value) == datetime(2026, 8, 4, 4, 30, tzinfo=UTC)


def test_as_utc_rejects_naive_values() -> None:
    value = datetime(2026, 8, 4, 12, 30)  # noqa: DTZ001

    with pytest.raises(ValueError, match="timezone information"):
        as_utc(value)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (
            datetime(
                2026,
                8,
                4,
                12,
                30,
                tzinfo=timezone(timedelta(hours=8)),
            ),
            datetime(2026, 8, 4, 4, 30, tzinfo=UTC),
        ),
        (
            datetime(
                2026,
                8,
                4,
                12,
                30,
                tzinfo=timezone(-timedelta(hours=5)),
            ),
            datetime(2026, 8, 4, 17, 30, tzinfo=UTC),
        ),
    ],
)
async def test_utc_datetime_round_trips_through_postgres(
    db_session: AsyncSession,
    value: datetime,
    expected: datetime,
) -> None:
    metadata = MetaData()
    timestamps = Table(
        "test_utc_timestamps",
        metadata,
        Column("value", UTCDateTime(), nullable=False),
    )
    connection = await db_session.connection()
    await connection.run_sync(metadata.create_all)

    await db_session.execute(insert(timestamps).values(value=value))
    await db_session.commit()

    stored_value = await db_session.scalar(select(timestamps.c.value))

    assert stored_value == expected
