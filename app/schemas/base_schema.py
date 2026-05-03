from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class IDMixinSchema(BaseModel):
    id: int


class TimeStampMixinSchema(BaseModel):
    created_at: datetime
    updated_at: datetime
