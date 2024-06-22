from ...env import getenv
from ...database import AsyncDatabaseConnection
from fastapi import APIRouter, Path
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get(
    "/api/users/@{name:str}",
    summary="ユーザーをユーザー名から取得します。",
    response_class=JSONResponse
)
async def getUserByName(name: str = Path(title="ユーザー名", min_length=1, max_length=14)):
    """
    ユーザーをユーザー名から取得します。
    """
    async with AsyncDatabaseConnection(getenv("dsn")) as conn:
        _user = await conn.fetchrow('SELECT * FROM users WHERE name = $1', name)
        if _user != None:
            user = dict(_user)
            user["detail"] = "success"
            del user["password"]
            return user
        else:
            return {
                "detail": "failed"
            }