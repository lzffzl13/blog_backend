from fastapi import FastAPI
from app.db.session import engine,Base
from app.models.user import User
from app.api.user import router as user_router

app = FastAPI()

app.include_router(user_router)
#创建表
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
@app.get("/")
def root():
    return {"message":"Welcome to Blog"}
