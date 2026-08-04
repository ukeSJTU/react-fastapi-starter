from datetime import datetime
from typing import Annotated

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    PlainSerializer,
)

from app.db.types import as_utc


def to_camel(value: str) -> str:
    first, *rest = value.split("_")
    return first + "".join(word.capitalize() for word in rest)


def serialize_utc_datetime(value: datetime) -> str:
    return as_utc(value).isoformat().replace("+00:00", "Z")


UTCDateTime = Annotated[
    datetime,
    AfterValidator(as_utc),
    PlainSerializer(serialize_utc_datetime, return_type=str, when_used="json"),
]


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        serialize_by_alias=True,
        validate_by_alias=True,
        validate_by_name=True,
    )
