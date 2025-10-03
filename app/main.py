from typing import Any, Dict

from api.api import api_router
from fastapi import FastAPI

app = FastAPI(
    title="Remote Flash API",
    description="遠隔書き込みシステム用のAPI",
    version="0.1.0",
)


app.include_router(api_router, prefix="/api", tags=["API"])


def main():
    import uvicorn

    uvicorn.run("main:app", port=8000, reload=True)


if __name__ == "__main__":
    main()
