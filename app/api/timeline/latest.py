from ...env import getenv
from ...database import AsyncDatabaseConnection
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get(
<<<<<<< HEAD
    "/api/letters/timeline/latest",
=======
    "/api/timeline/latest",
>>>>>>> f12de26a8cc42a8924e75eb7d9b8c31711c2610c
    summary="最新のレターの一覧を取得します。",
    response_class=JSONResponse
)
async def latest(page: int = Query(title="ページ", default=0, ge=0)):
    """
    最新のレターの一覧を取得します。
    """
    async with AsyncDatabaseConnection(getenv("dsn")) as conn:
<<<<<<< HEAD
        _letters = await conn.fetch('SELECT * FROM letters ORDER BY created_at DESC LIMIT 20 OFFSET $1', page*20)
=======
        _letters = await conn.fetch('SELECT * FROM letters LIMIT 20 OFFSET $1', page*20)
>>>>>>> f12de26a8cc42a8924e75eb7d9b8c31711c2610c
        count = len(_letters)
        letters = {}
        letters["letters"] = []
        for letter in _letters:
            letter = dict(letter)
            letter["id"] = str(letter["id"])
            letter["userid"] = str(letter["userid"])
            letters["letters"].append(letter)
        letters["next"] = f"https://nyantter.f5.si/api/timeline/latest?page={page+1}"
        return letters