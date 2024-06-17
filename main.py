from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import logging

from app.api import nyantterstat
from app.api.auth import register, login, logout
from app.api.letters import post, edit, delete
from app.api.timeline import latest
from app.api.users import getUserByName, getUserByID, me

from app import frontend

log = logging.getLogger("uvicorn")

log.info("Nyantter is loading now...")

@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Nyantter was loaded!")
    yield
    log.info("Nyantter is stopping...")

app = FastAPI(
    title="Nyantter",
    version="2024.06.14",
    summary="猫たちの、猫たちによる、猫たちのためのSNSです。本APIでは、Nyantterのほとんどすべて(いや、ほんの少しかも)を操作することができます。 ",
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
app.include_router(logout.router)

app.include_router(post.router)
app.include_router(edit.router)
app.include_router(delete.router)

app.include_router(latest.router)

app.include_router(getUserByName.router)
app.include_router(getUserByID.router)
app.include_router(me.router)

app.include_router(frontend.router)