from ...env import getenv
from ...database import AsyncDatabaseConnection
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get(
    "/api/timeline/latest",
    summary="最新のレターの一覧を取得します。",
    response_class=JSONResponse
)
async def latest(page: int = Query(title="ページ", default=0, ge=0)):
    """
    最新のレターの一覧を取得します。
    """
    async with AsyncDatabaseConnection(getenv("dsn")) as conn:
        _letters = await conn.fetch('SELECT * FROM letters LIMIT 20 OFFSET $1', page*20)
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