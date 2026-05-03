from pydantic import BaseModel


class PaginationSchema[T](BaseModel):
    page: int
    size: int
    items: list[T]
    total_items: int
    total_pages: int
