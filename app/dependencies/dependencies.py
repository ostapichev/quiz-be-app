from fastapi import Request

from app.services import RedisService


def get_redis_service(request: Request) -> RedisService:
    return request.app.state.redis
