import math

from fastapi import Query


class PaginationConfig:
    def __init__(
        self,
        page: int = Query(1, ge=1, description="page"),
        size: int = Query(10, ge=1, le=50, description="size"),
    ) -> None:
        self.page: int = page
        self.size: int = size

    @property
    def skip(self) -> int:
        return (self.page - 1) * self.size

    @property
    def limit(self) -> int:
        return self.size

    def get_total_pages(self, total_items: int) -> int:
        return math.ceil(total_items / self.size)
