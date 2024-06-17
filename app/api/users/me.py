from ...env import getenv
from ...database import AsyncDatabaseConnection
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get(
    "/api/users/me",
    summary="トークンからユーザーを取得します。",
    response_class=JSONResponse
)
async def getUserByName(request: Request):
    """
    トークンからユーザーを取得します。
    """
    token = request.headers.get("Authorization", "")

    async with AsyncDatabaseConnection(getenv("dsn")) as conn:
        # トークンの認証とユーザーIDの取得
        user_id = await conn.fetchval('SELECT userid FROM token WHERE token = $1', token)
        if not user_id:
            raise HTTPException(status_code=401, detail="Login Required")

        _user = await conn.fetchrow('SELECT * FROM users WHERE id = $1', user_id)
        if _user != None:
            user = dict(_user)
            user["detail"] = "success"
            del user["password"]
            return user
        else:
            return {
                "detail": "failed"
            }