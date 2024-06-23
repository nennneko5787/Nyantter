from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import bcrypt
from snowflake import SnowflakeGenerator
from datetime import datetime
import re

from ...database import AsyncDatabaseConnection
from ...turnstile import verify_captcha
from ...generator import random_text
from ...env import getenv

import logging

log = logging.getLogger("uvicorn")

def name_check(username):
    # ユーザー名に許可されている文字以外が含まれているかをチェックする正規表現
    pattern = re.compile(r'[^a-zA-Z0-9_.-]')
    return bool(pattern.search(username))

router = APIRouter()

class WillRegistUser(BaseModel):
    name: str
    password: str
    password_confirm: str
    turnstile: str

@router.post(
    "/api/auth/register",
    response_class=JSONResponse,
    include_in_schema=False,
)
async def register(request: Request, user: WillRegistUser):
    forwarded_for = request.headers.get('X-Forwarded-For')

    if forwarded_for:
        ipaddr = forwarded_for.split(',')[0]  # 複数のIPアドレスがカンマ区切りで送信される場合があるため、最初のものを取得
    else:
        ipaddr = request.client.host

    if name_check(user.name):
        raise HTTPException(status_code=400, detail="Username contains invalid characters")
    
    if len(user.name) < 0 and len(user.name) > 14:
        raise HTTPException(status_code=400, detail="Username must be at least 1 and no more than 14 characters long")

    if user.password != user.password_confirm:
        raise HTTPException(status_code=400, detail="Passwords don't match")

    if not await verify_captcha(user.turnstile):
        raise HTTPException(status_code=400, detail="Failed to verify captcha")

    salt = bcrypt.gensalt(rounds=10, prefix=b'2a')
    hashed_password = bcrypt.hashpw(user.password.encode(), salt).decode()

    async with AsyncDatabaseConnection(getenv("dsn")) as conn:
        ipbanned = await conn.fetchrow('SELECT * FROM ban WHERE ipaddr = $1', ipaddr)
        if ipbanned:
            raise HTTPException(status_code=403, detail=f"IP address banned: {ipbanned['reason']} ({ipbanned['banned_at']})")

        if await conn.fetchval('SELECT EXISTS(SELECT 1 FROM users WHERE name = $1)', user.name):
            raise HTTPException(status_code=400, detail="User exists")

        gen = SnowflakeGenerator(1, timestamp=int(datetime.now().timestamp()))
        user_id = next(gen)

        await conn.execute(
            """
            INSERT INTO users (id, name, password) VALUES ($1, $2, $3)
            """,
            user_id, user.name, hashed_password
        )

        token = random_text(46)

        await conn.execute(
            """
            INSERT INTO token (token, userid) VALUES ($1, $2)
            """,
            token, user_id
        )

    log.info(f"{ipaddr} > registed {user.name} ({user_id})")
    return {"detail": "Registered", "token": token, "userid": str(user_id)}
