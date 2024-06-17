from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .env import getenv

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("index.html", context)

@router.get("/register", response_class=HTMLResponse, include_in_schema=False)
async def register(request: Request):
    context = {"request": request, "turnstile_sitekey": getenv("turnstile_sitekey")}
    return templates.TemplateResponse("register.html", context)

@router.get("/login", response_class=HTMLResponse, include_in_schema=False)
async def register(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("login.html", context)

@router.get("/home", response_class=HTMLResponse, include_in_schema=False)
async def home(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("home.html", context)