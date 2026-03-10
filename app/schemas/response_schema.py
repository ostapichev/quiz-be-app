from pydantic import BaseModel


class ResponseSchema(BaseModel):
    status_code: int
    detail: str
    result: str
