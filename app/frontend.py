from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="templates")

<<<<<<< HEAD:app/frontend.py
@router.get("/home", response_class=HTMLResponse, include_in_schema=False)
=======
@router.get("/", response_class=HTMLResponse, include_in_schema=False)
>>>>>>> 8fb46f29e93aeef6ee8eb31a3c1dcd729137cb52:app/frontend/index.py
async def read_root(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("home.html", context)