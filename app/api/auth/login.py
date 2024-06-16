from ...database import AsyncDatabaseConnection
from ...generator import random_text
from ...env import getenv
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import bcrypt

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
async def login(response: Response, user: WillLoginUser):
    """
    ユーザー名とパスワードを使用してログインします。
    ※このエンドポイントは**非推奨**です！代わりに提供される予定のoAuth2を使用してください！
    """
    async with AsyncDatabaseConnection(getenv("dsn")) as conn:
        user_exists = await conn.fetchval('SELECT EXISTS(SELECT 1 FROM users WHERE name = $1)', user.name)
        if not user_exists:
            raise HTTPException(status_code=403, detail="Username or password incorrect")

        row = await conn.fetchrow('SELECT id, password FROM users WHERE name = $1', user.name)
        if not bcrypt.checkpw(user.password.encode(), row["password"].encode()):
            raise HTTPException(status_code=403, detail="Username or password incorrect")

        token = random_text(46)

        await conn.execute(
            """
            INSERT INTO token (token, userid) VALUES ($1, $2)
            """,
            token, row["id"]
        )
        response.set_cookie(
            key="token",
            value=token,
            secure=True,
            httponly=False,
        )

    return {"detail": "Logged in", "token": token}
