from fastapi import status, HTTPException

from app.schemas import ResponseSchema
from app.services import RedisService


class ResponseService:
    CACHE_KEY = "response"
    DETAIL = "ok"
    RESULT = "working"

    def __init__(self, redis_client: RedisService) -> None:
        self.redis_client = redis_client

    def get_response(self) -> ResponseSchema:
        return ResponseSchema(
            status_code=status.HTTP_200_OK,
            detail=self.DETAIL,
            result=self.RESULT,
        )

    async def create_cache_response(self, detail, result) -> ResponseSchema:
        await self.redis_client.hset(
            self.CACHE_KEY,
            status_code=status.HTTP_200_OK,
            detail=detail,
            result=result,
        )
        return await self.get_cache_response()

    async def get_cache_response(self) -> ResponseSchema:
        response = await self.redis_client.hgetall(self.CACHE_KEY)
        self._not_found_response(response)
        return ResponseSchema(**response)

    async def delete_cache_response(self) -> None:
        deleted = await self.redis_client.delete(self.CACHE_KEY)
        self._not_found_response(deleted)

    @staticmethod
    def _not_found_response(response: ResponseSchema | bool) -> None:
        if not response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found",
            )
