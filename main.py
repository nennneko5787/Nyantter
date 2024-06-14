from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import logging

from app.api import nekotterstat
from app.api.auth import register
from app.api.auth import login
from app.api.letters import post
from app.api.letters import edit
from app.api.letters import delete

from app.frontend import index

log = logging.getLogger("uvicorn")

log.info("Nyantter is loading now...")

@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Nyantter was loaded!")
    yield
    log.info("Nyantter is stopping...")
    
app = FastAPI(
    title="Nyantter",
    version="v2024.06.14",
    lifespan=lifespan
)
app.mount(path="/static", app=StaticFiles(directory="static"), name="static")

app.include_router(nekotterstat.router)
app.include_router(register.router)
app.include_router(login.router)
app.include_router(post.router)
app.include_router(edit.router)
app.include_router(delete.router)

app.include_router(index.router)