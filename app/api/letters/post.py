from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from snowflake import SnowflakeGenerator
from datetime import datetime
import html
from typing import Optional, Union
from ...env import getenv
from ...database import AsyncDatabaseConnection
import re

import logging

log = logging.getLogger("uvicorn")

router = APIRouter()

class WillPostLetter(BaseModel):
    content: str
    replyed_to: Optional[Union[int, str]] = None
    relettered_to: Optional[Union[int, str]] = None

@router.post(
    "/api/letters",
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
    forwarded_for = request.headers.get('X-Forwarded-For')

    if forwarded_for:
        ipaddr = forwarded_for.split(',')[0]  # 複数のIPアドレスがカンマ区切りで送信される場合があるため、最初のものを取得
    else:
        ipaddr = request.client.host

    token = request.headers.get("Authorization", "")
    if letter.relettered_to is None and letter.content == "":
        raise HTTPException(status_code=400, detail="content Required")
    
    if letter.relettered_to is not None and letter.replyed_to is not None:
        raise HTTPException(status_code=400, detail="What is \"Relettered Reply\"?")

    if len(letter.content) > 222:
        raise HTTPException(status_code=413, detail="Content too large")

    async with AsyncDatabaseConnection(getenv("dsn")) as conn:
        ipbanned = await conn.fetchrow('SELECT * FROM ban WHERE ipaddr = $1', ipaddr)
        if ipbanned:
            raise HTTPException(status_code=403, detail=f"IP address banned: {ipbanned['reason']} ({ipbanned['banned_at']})")

        # トークンの認証
        user_id = await conn.fetchval('SELECT userid FROM token WHERE token = $1', token)
        if not user_id:
            raise HTTPException(status_code=401, detail="Login Required")

        # ユーザーの存在確認
        user_exists = await conn.fetchval('SELECT EXISTS(SELECT 1 FROM users WHERE id = $1)', user_id)
        if not user_exists:
            raise HTTPException(status_code=401, detail="User not found")

        replyed_to = int(letter.replyed_to) if letter.replyed_to is not None else None
        relettered_to = int(letter.relettered_to) if letter.relettered_to is not None else None

        if replyed_to is not None:
            letter_exists = await conn.fetchval('SELECT EXISTS(SELECT 1 FROM letters WHERE id = $1)', replyed_to)
            if not letter_exists:
                raise HTTPException(status_code=401, detail="Letter not found")
        
        if relettered_to is not None:
            letter_exists = await conn.fetchval('SELECT EXISTS(SELECT 1 FROM letters WHERE id = $1)', relettered_to)
            if not letter_exists:
                raise HTTPException(status_code=401, detail="Letter not found")

        # レターIDの生成
        gen = SnowflakeGenerator(1, timestamp=int(datetime.now().timestamp()))
        letter_id = next(gen)

        content = re.sub(r'(\r\n|\r|\n)', '<br>\n', html.escape(letter.content))
        content = re.sub(r'(?i)\$\[ruby\|([^|]+)\|(.+)\]', r'<ruby>\1<rp>(</rp><rt>\2</rt><rp>)</rp></ruby>', content)
        content = re.sub(r'(?i)\$\[color=([^|]+)\|(.+)\]', r'<span style="color: \1">\2</span>', content)
        content = re.sub(r'(?i)\$\[bgColor=([^|]+)\|(.+)\]', r'<span style="background-color: \1">\2</span>', content)
        content = re.sub(r'\*\*([^\*]+)\*\*', r'<b>\1</b>', content)
        content = re.sub(r'__([^_]+)__', r'<u>\1</u>', content)
        content = re.sub(r'\*([^\*]+)\*', r'<i>\1</i>', content)
        content = re.sub(r'~~([^~]+)~~', r'<s>\1</s>', content)

        # レターの投稿
        await conn.execute(
            """
            INSERT INTO letters (id, userid, content, replyed_to, relettered_to)
            VALUES ($1, $2, $3, $4, $5)
            """,
            letter_id, user_id, content, replyed_to, relettered_to
        )

    log.info(f"{ipaddr} > posted {letter_id}")
    return JSONResponse(
        {"detail": "Posted", "id": str(letter_id)},
        200
    )
