from ..env import getenv
from ..database import AsyncDatabaseConnection
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/api/stat", response_class=JSONResponse)
async def stat():
    async with AsyncDatabaseConnection(getenv("dsn")) as conn:
        users = await conn.fetchval('SELECT COUNT(*) FROM users')
        letters = await conn.fetchval('SELECT COUNT(*) FROM letters')
        return {
            "users": users,
            "letters": letters
        }