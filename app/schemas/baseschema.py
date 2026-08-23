import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
    )


class IDMixinSchema(BaseModel):
    id: int
    public_id: uuid.UUID


class TimeStampMixinSchema(BaseModel):
    created_at: datetime
    updated_at: datetime
