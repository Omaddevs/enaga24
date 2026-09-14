from aiogram import Router

from app.handlers import admin, groups, listings, users


def setup_routers() -> Router:
    root = Router()
    root.include_router(admin.router)
    root.include_router(groups.router)
    root.include_router(users.router)
    root.include_router(listings.router)
    return root
