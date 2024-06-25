from ...database import AsyncDatabaseConnection
from ...generator import random_text
from ...env import getenv
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import bcrypt

import logging

log = logging.getLogger("uvicorn")

router = APIRouter()

class WillLoginUser(BaseModel):
    name: str
    password: str

@router.post(
    "/api/auth/login",
    summary="ユーザー名とパスワードを使用してログインします。",
    response_class=JSONResponse,
    deprecated=True,
)
async def login(request: Request, user: WillLoginUser):
    """
    ユーザー名とパスワードを使用してログインします。
    ※このエンドポイントは**非推奨**です！代わりに提供される予定のOAuth2を使用してください！
    """
    forwarded_for = request.headers.get('X-Forwarded-For')

    if forwarded_for:
        ipaddr = forwarded_for.split(',')[0]  # 複数のIPアドレスがカンマ区切りで送信される場合があるため、最初のものを取得
    else:
        ipaddr = request.client.host

    async with AsyncDatabaseConnection(getenv("dsn")) as conn:
        ipbanned = await conn.fetchrow('SELECT * FROM ban WHERE ipaddr = $1', ipaddr)
        if ipbanned:
            raise HTTPException(status_code=403, detail=f"IP address banned: {ipbanned['reason']} ({ipbanned['banned_at']})")

        user_exists = await conn.fetchval('SELECT EXISTS(SELECT 1 FROM users WHERE name = $1)', user.name)
        if not user_exists:
            raise HTTPException(status_code=403, detail="Username or password incorrect")

        row = await conn.fetchrow('SELECT id, password FROM users WHERE name = $1', user.name)
        if not bcrypt.checkpw(user.password.encode(), row["password"].encode()):
            raise HTTPException(status_code=403, detail="Username or password incorrect")

        if row.get("isfreezing", false):
            raise HTTPException(status_code=403, detail="Account is freezing")

        token = random_text(46)

        await conn.execute(
            """
            INSERT INTO token (token, userid) VALUES ($1, $2)
            """,
            token, row["id"]
        )

    log.info(f"{ipaddr} > logined {user.name} ({row['id']})")
    return {"detail": "Logged in", "token": token, "userid": str(row["id"])}
