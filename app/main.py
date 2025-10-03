from fastapi import FastAPI

from app.api.api import api_router

app = FastAPI(
    title="Remote Flash API",
    description="遠隔書き込みシステム用のAPI",
    version="0.1.0",
)


app.include_router(api_router, prefix="/api", tags=["API"])
