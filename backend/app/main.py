"""
main.py — FastAPI application factory.
Mounts all routers and serves the frontend static files.
"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.routes.auth_routes import router as auth_router
from backend.routes.node_routes import router as node_router
from backend.routes.server_routes import router as server_router
from backend.utils.logger import get_logger

log = get_logger("main")

FRONTEND_DIR = Path(__file__).parent.parent.parent / "frontend"


def create_app() -> FastAPI:
    app = FastAPI(
        title="MC Panel API",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # API routers
    app.include_router(auth_router, prefix="/api")
    app.include_router(node_router, prefix="/api")
    app.include_router(server_router, prefix="/api")

    # Serve frontend static files
    if FRONTEND_DIR.exists():
        app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
        log.info("Serving frontend from %s", FRONTEND_DIR)
    else:
        log.warning("Frontend directory not found at %s", FRONTEND_DIR)

    return app


app = create_app()
