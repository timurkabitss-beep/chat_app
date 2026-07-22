from backend.routers.auth import router as auth_router
from backend.routers.users import router as users_router
from backend.routers.messages import router as messages_router
from backend.routers.groups import router as groups_router

__all__ = ["auth_router", "users_router", "messages_router", "groups_router"]
