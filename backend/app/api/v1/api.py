from fastapi import APIRouter
from .endpoints import infrastructure, observability, users, deployments, costs

api_router = APIRouter()

api_router.include_router(infrastructure.router, prefix="/infrastructure", tags=["infrastructure"])
api_router.include_router(observability.router, prefix="/observability", tags=["observability"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(deployments.router, prefix="/deployments", tags=["deployments"])
api_router.include_router(costs.router, prefix="/costs", tags=["costs"])
