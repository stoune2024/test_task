from fastapi import FastAPI, Request
from app.routers.db import router as db_router
import time

app = FastAPI()

app.include_router(db_router)