from pydantic import BaseModel


class Pagination[T](BaseModel):
    page: int
    size: int
    items: list[T]
    total_items: int
    total_pages: int
