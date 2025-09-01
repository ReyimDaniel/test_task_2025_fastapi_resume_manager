import uvicorn
from fastapi import FastAPI
from app_v1.controllers.user_controller import router as user_router
from app_v1.controllers.resume_controller import router as resume_router
from app_v1.core.db_helper import DataBaseHelper
from app_v1.models.base import Base

db_helper = DataBaseHelper(
    url="postgresql+asyncpg://user:886688zsewdc@localhost:5432/resume_database",
    echo=True
)

app = FastAPI(title="FastAPI V1")
app.include_router(router=user_router, prefix='/users')
app.include_router(router=resume_router, prefix='/resumes')


@app.on_event("startup")
async def on_startup():
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/")
def hello_world():
    return {
        "message": "Hello World!"
    }


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
