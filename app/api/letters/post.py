from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from snowflake import SnowflakeGenerator
from datetime import datetime
import html
from typing import Optional
from ...env import getenv
from ...database import AsyncDatabaseConnection

router = APIRouter()

class Post(BaseModel):
    content: str
    replyed_to: Optional[int] = None
    relettered_to: Optional[int] = None

@router.post(
    "/api/letters/post",
    summary="Post a letter.",
    response_class=JSONResponse
)
async def post_letter(request: Request, letter: Post):
    """
    Post a letter with all the infomation:
    
    - **content**: body of letter.
    - **replyed_to**: If the letter you are submitting is a reply to another letter, specify the Snowflake ID for that letter here.
    - **relettered_to**: If the letter you are submitting is a "reletter" to another letter, please specify the letter's Snowflake ID here.
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

        # レターの投稿
        await conn.execute(
            """
            INSERT INTO letters (id, userid, content, replyed_to, relettered_to)
            VALUES ($1, $2, $3, $4, $5)
            """,
            letter_id, user_id, html.escape(letter.content), letter.replyed_to, letter.relettered_to
        )

    return JSONResponse(
        {"detail": "Posted", "id": letter_id},
        201
    )
