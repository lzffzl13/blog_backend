from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.article import router as article_router
from app.api.auth import router as auth_router
from app.api.category import router as category_router
from app.api.comment import router as comment_router
from app.api.tag import router as tag_router
from app.api.user import router as user_router
from app.core.config import settings
from app.core.exceptions import AppException
from app.core.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    setup_logging()

    yield
    # 关闭时执行


app = FastAPI(lifespan=lifespan)


# 全局异常处理器
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": {
                "code": exc.error_code or "UNKNOWN_ERROR",
                "message": exc.detail,
            }
        },
    )


app.include_router(user_router)
app.include_router(article_router)
app.include_router(auth_router)
app.include_router(category_router)
app.include_router(tag_router)
app.include_router(comment_router)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Welcome to Blog"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
