from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import bcrypt
from snowflake import SnowflakeGenerator
from datetime import datetime

from ...database import AsyncDatabaseConnection
from ...turnstile import verify_captcha
from ...generator import random_text
from ...env import getenv

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
async def register(response: Response, user: WillRegistUser):
    if user.password != user.password_confirm:
        raise HTTPException(status_code=400, detail="Passwords don't match")

    if not await verify_captcha(user.turnstile):
        raise HTTPException(status_code=400, detail="Failed to verify captcha")

    salt = bcrypt.gensalt(rounds=10, prefix=b'2a')
    hashed_password = bcrypt.hashpw(user.password.encode(), salt).decode()

    async with AsyncDatabaseConnection(getenv("dsn")) as conn:
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
        response.set_cookie(
            key="token",
            value=token,
            secure=True,
            httponly=False,
        )

    return {"detail": "Registered", "token": token}
