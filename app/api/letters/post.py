from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from snowflake import SnowflakeGenerator
from datetime import datetime
import html
<<<<<<< HEAD
from typing import Optional, Union
from ...env import getenv
from ...database import AsyncDatabaseConnection
import re
=======
from typing import Optional
from ...env import getenv
from ...database import AsyncDatabaseConnection
>>>>>>> f12de26a8cc42a8924e75eb7d9b8c31711c2610c

router = APIRouter()

class WillPostLetter(BaseModel):
    content: str
<<<<<<< HEAD
    replyed_to: Optional[Union[int, str]] = None
    relettered_to: Optional[Union[int, str]] = None

@router.post(
    "/api/letters",
=======
    replyed_to: Optional[int] = None
    relettered_to: Optional[int] = None

@router.post(
    "/api/letters/post",
>>>>>>> f12de26a8cc42a8924e75eb7d9b8c31711c2610c
    summary="レターを「ポストボックス」に入れます。",
    response_class=JSONResponse,
)
async def post_letter(request: Request, letter: WillPostLetter):
    """
    以下のパラメータを指定して、レターを「ポストボックス」にいれます。  
      
    - **content**: レターの本文。  
    - **replyed_to**: 返信先ポスト。  
    - **relettered_to**: リレター先ポスト。  
    """
    token = request.headers.get("Authorization", "")

    async with AsyncDatabaseConnection(getenv("dsn")) as conn:
        # トークンの認証
        user_id = await conn.fetchval('SELECT userid FROM token WHERE token = $1', token)
        if not user_id:
            raise HTTPException(status_code=401, detail="Login Required")

        # ユーザーの存在確認
        user_exists = await conn.fetchval('SELECT EXISTS(SELECT 1 FROM users WHERE id = $1)', user_id)
        if not user_exists:
            raise HTTPException(status_code=401, detail="User not found")

        # レターIDの生成
        gen = SnowflakeGenerator(1, timestamp=int(datetime.now().timestamp()))
        letter_id = next(gen)

<<<<<<< HEAD
        content = re.sub(r'(\r\n|\r|\n)', '<br>\n', html.escape(letter.content))
        content = re.sub(r'\$\[ruby\|(.*?)\|(.*?)\]', r'<ruby>\1<rp>(</rp><rt>\2</rt><rp>)</rp></ruby>', content)

        replyed_to = int(letter.replyed_to) if letter.replyed_to is not None else None
        relettered_to = int(letter.relettered_to) if letter.relettered_to is not None else None

=======
>>>>>>> f12de26a8cc42a8924e75eb7d9b8c31711c2610c
        # レターの投稿
        await conn.execute(
            """
            INSERT INTO letters (id, userid, content, replyed_to, relettered_to)
            VALUES ($1, $2, $3, $4, $5)
            """,
<<<<<<< HEAD
            letter_id, user_id, content, replyed_to, relettered_to
=======
            letter_id, user_id, html.escape(letter.content), letter.replyed_to, letter.relettered_to
>>>>>>> f12de26a8cc42a8924e75eb7d9b8c31711c2610c
        )

    return JSONResponse(
        {"detail": "Posted", "id": str(letter_id)},
        201
    )
