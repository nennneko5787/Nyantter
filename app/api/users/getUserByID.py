from ...env import getenv
from ...database import AsyncDatabaseConnection
from fastapi import APIRouter, Path
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get(
    "/api/users/{id:int}",
    summary="ユーザーをユーザーID(Snowflake)から取得します。",
    response_class=JSONResponse
)
async def getUserByName(id: int):
    """
    ユーザーをユーザー名ID(Snowflake)から取得します。
    """
    async with AsyncDatabaseConnection(getenv("dsn")) as conn:
        _user = await conn.fetchrow('SELECT * FROM users WHERE id = $1', id)
        if _user != None:
            user = dict(_user)
            user["detail"] = "success"
            del user["password"]
            return user
        else:
            return {
                "detail": "failed"
            }