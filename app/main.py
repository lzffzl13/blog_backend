from fastapi import FastAPI
from app.db.session import engine,Base
from app.models.user import User

app = FastAPI()
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
@app.get("/")
def root():
    return {"message":"Welcome to Blog"}
