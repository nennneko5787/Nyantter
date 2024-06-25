from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import html
from ...env import getenv
from ...database import AsyncDatabaseConnection
import re
import html

router = APIRouter()

class WillEditPost(BaseModel):
    content: str

@router.patch(
    "/api/letters/{letter_id:int}/edit",
    summary="レターを編集します。",
    response_class=JSONResponse
)
async def edit_letter(request: Request, letter_id: int, letter: WillEditPost):
    """
    以下のパラメータを指定して、「ポストボックス」にいれたレターを編集します。  
      
    - **content**: レターの本文。
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

        content = re.sub(r'(\r\n|\r|\n)', '<br>\n', html.escape(letter.content))
        content = re.sub(r'(?i)\$\[ruby\|([^|]+)\|(.+)\]', r'<ruby>\1<rp>(</rp><rt>\2</rt><rp>)</rp></ruby>', content)
        content = re.sub(r'(?i)\$\[color=([^|]+)\|(.+)\]', r'<span style="color: \1">\2</span>', content)
        content = re.sub(r'(?i)\$\[bgColor=([^|]+)\|(.+)\]', r'<span style="background-color: \1">\2</span>', content)
        content = re.sub(r'\*\*([^\*]+)\*\*', r'<b>\1</b>', content)
        content = re.sub(r'__([^_]+)__', r'<u>\1</u>', content)
        content = re.sub(r'\*([^\*]+)\*', r'<i>\1</i>', content)
        content = re.sub(r'~~([^~]+)~~', r'<s>\1</s>', content)

        # レターの編集
        await conn.execute(
            """
            UPDATE letters
            SET content = $1, edited_at = now()
            WHERE id = $2 AND userid = $3
            """,
            content, letter_id, user_id
        )

    return JSONResponse(
        {"detail": "Edited"},
        200
    )
