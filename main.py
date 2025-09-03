from pathlib import Path
import uvicorn
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse

from app_v1.controllers.user_controller import router as user_router
from app_v1.controllers.resume_controller import router as resume_router
from app_v1.auth.controller.jwt_controller import router as jwt_router
from app_v1.controllers.web_resume_controller import router as web_router
from app_v1.core.db_helper import DataBaseHelper
from app_v1.models.base import Base
from app_v1.core.config import settings


db_helper = DataBaseHelper(
    url=settings.db_url,
    echo=settings.db_echo
)

app = FastAPI(title="FastAPI V1")
app.include_router(router=user_router, prefix='/users')
app.include_router(router=resume_router, prefix='/resumes')
app.include_router(router=jwt_router, prefix='/auth')
app.include_router(router=web_router)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@app.on_event("startup")
async def on_startup():
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/")
async def root():
    return RedirectResponse(url="/login")


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
