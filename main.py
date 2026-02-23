from __future__ import annotations

import os
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.config.settings import Settings
from app.utils.logging import configure_logging


def create_app(settings: Settings) -> FastAPI:
    configure_logging(settings=settings)

    app = FastAPI(title="Museum Exhibits", debug=settings.stage == "dev")

    os.makedirs(settings.photos_dir, exist_ok=True)
    static_dir = os.path.join(os.path.dirname(__file__), "app", "api", "static")
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    app.mount("/photos", StaticFiles(directory=settings.photos_dir), name="photos")
    app.include_router(router)
    return app


def main() -> None:
    settings = Settings()
    app = create_app(settings=settings)

    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_config=None,
    )


if __name__ == "__main__":
    main()
