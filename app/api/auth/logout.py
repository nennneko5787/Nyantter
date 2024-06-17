from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import html
from ...env import getenv
from ...database import AsyncDatabaseConnection

router = APIRouter()

@router.delete(
    "/api/auth/logout",
    response_class=JSONResponse,
    include_in_schema=False,
)
async def delete_letter(request: Request,):
    token = request.headers.get("Authorization", "")

    async with AsyncDatabaseConnection(getenv("dsn")) as conn:
        # トークンの認証とユーザーIDの取得
        user_id = await conn.fetchval('SELECT userid FROM token WHERE token = $1', token)
        if not user_id:
            raise HTTPException(status_code=401, detail="Login Required")

        # レターの編集
        await conn.execute(
            """
            DELETE from token
            WHERE token = $1
            """,
            token
        )

    return JSONResponse(
        {"detail": "deleted"},
        200
    )
