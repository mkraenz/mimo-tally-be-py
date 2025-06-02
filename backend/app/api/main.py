from fastapi import APIRouter

from app.api.routes import (
    disbursements,
    settlements,
    users,
    utils,
)

api_router = APIRouter()
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(disbursements.router)
api_router.include_router(settlements.router)
