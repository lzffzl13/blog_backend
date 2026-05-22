from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.article import router as article_router
from app.api.user import router as user_router
from app.core.logging import setup_logging
from app.db.session import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    setup_logging()
    Base.metadata.create_all(bind=engine)
    yield
    # 关闭时执行


app = FastAPI(lifespan=lifespan)
app.include_router(user_router)
app.include_router(article_router, prefix="/articles")


@app.get("/")
def root():
    return {"message": "Welcome to Blog"}
