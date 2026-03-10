from fastapi import Depends, Request

from app.services import ResponseService, RedisService


def get_redis_service(request: Request) -> RedisService:
    return request.app.state.redis


def get_response_service(
    redis_client: RedisService = Depends(get_redis_service),
) -> ResponseService:
    return ResponseService(redis_client)
