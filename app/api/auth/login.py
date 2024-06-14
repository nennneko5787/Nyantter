from ...database import AsyncDatabaseConnection
from ...generator import random_text
from ...env import getenv
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import bcrypt

router = APIRouter()

class WillLoginUser(BaseModel):
    name: str
    password: str

@router.post(
    "/api/auth/login",
    summary="Login with username and password",
    response_class=JSONResponse,
)
async def login(user: WillLoginUser):
    """
    Login with your username and password.
    **This endpoint is deprecated! Please use oAuth2 instead!**
    """
    async with AsyncDatabaseConnection(getenv("dsn")) as conn:
        user_exists = await conn.fetchval('SELECT EXISTS(SELECT 1 FROM users WHERE name = $1)', user.name)
        if not user_exists:
            raise HTTPException(status_code=400, detail="Username or password incorrect")

        row = await conn.fetchrow('SELECT id, password FROM users WHERE name = $1', user.name)
        if not bcrypt.checkpw(user.password.encode(), row["password"].encode()):
            raise HTTPException(status_code=400, detail="Username or password incorrect")

        token = random_text(46)

        await conn.execute(
            """
            INSERT INTO token (token, userid) VALUES ($1, $2)
            """,
            token, row["id"]
        )

    return {"detail": "Logged in", "token": token}
