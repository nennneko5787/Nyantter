from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import html
from ...env import getenv
from ...database import AsyncDatabaseConnection

router = APIRouter()

@router.delete(
    "/api/letters/{letter_id:int}/delete",
    summary="「ポストボックス」にいれたレターを削除します。",
    response_class=JSONResponse,
)
async def delete_letter(request: Request, letter_id: int):
    """
    「ポストボックス」にいれたレターを削除します。
    """
    token = request.headers.get("Authorization", "")

    async with AsyncDatabaseConnection(getenv("dsn")) as conn:
        ipbanned = await conn.fetchrow('SELECT * FROM ban WHERE ipaddr = $1', ipaddr)
        if ipbanned:
            raise HTTPException(status_code=403, detail=f"IP address banned: {ipbanned['reason']} ({ipbanned['banned_at']})")

        # トークンの認証とユーザーIDの取得
        user_id = await conn.fetchval('SELECT userid FROM token WHERE token = $1', token)
        if not user_id:
            raise HTTPException(status_code=401, detail="Login Required")

        # レターの存在と所有権の確認
        letter_exists = await conn.fetchval(
            'SELECT EXISTS(SELECT 1 FROM letters WHERE id = $1 AND userid = $2)', letter_id, user_id)
        if not letter_exists:
            raise HTTPException(status_code=403, detail="The specified letter is not yours or does not exist")

        # レターの編集
        await conn.execute(
            """
            DELETE from letters
            WHERE id = $1 AND userid = $2
            """,
            letter_id, user_id
        )

    return JSONResponse(
        {"detail": "deleted"},
        200
    )
