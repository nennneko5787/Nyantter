from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import logging

from app.api import nyantterstat
from app.api.auth import register
from app.api.auth import login
from app.api.letters import post
from app.api.letters import edit
from app.api.letters import delete

from app import frontend

log = logging.getLogger("uvicorn")

log.info("Nyantter is loading now...")

@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Nyantter was loaded!")
    yield
    log.info("Nyantter is stopping...")
    
with open("NyantterAPISummary.md", "r") as f:
    summary = f.read()

app = FastAPI(
    title="Nyantter",
    version="2024.06.14",
    summary=summary,
    contact={
        "name": "nennneko5787",
        "url": "http://nennneko5787.cloudfree.jp/",
        "email": "nennneko5787@14chan.jp",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    lifespan=lifespan
)
app.mount(path="/static", app=StaticFiles(directory="static"), name="static")

app.include_router(nyantterstat.router)
app.include_router(register.router)
app.include_router(login.router)
app.include_router(post.router)
app.include_router(edit.router)
app.include_router(delete.router)

app.include_router(frontend.router)