from __future__ import annotations

import logging
import os
from typing import Optional

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config.settings import Settings
from app.services.exhibits_service import get_exhibit, list_exhibits, with_safe_photo
from app.utils.errors import InfraError


logger = logging.getLogger(__name__)

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "app", "api", "templates")

templates = Jinja2Templates(directory=TEMPLATES_DIR)


def _get_photo_url(exhibit, settings: Settings) -> str | None:
    candidates = [f"{exhibit.exhibit_id}{ext}" for ext in (".png", ".jpg", ".jpeg", ".webp")]
    if exhibit.photo_file:
        candidates.append(exhibit.photo_file)

    for filename in candidates:
        safe_name = filename.replace("..", "").replace("\\", "/")
        photo_fs_path = os.path.join(settings.photos_dir, safe_name)
        if os.path.exists(photo_fs_path):
            return f"/photos/{safe_name}"
    return None


@router.get("/", response_class=HTMLResponse)
def index(
    request: Request,
    q: Optional[str] = None,
) -> HTMLResponse:
    settings = Settings()

    logger.info("list_exhibits", extra={"stage": "web"})

    try:
        exhibits = [
            with_safe_photo(e)
            for e in list_exhibits(
                xlsx_path=settings.xlsx_path,
                q=q,
                museum=None,
                category=None,
            )
        ]
    except InfraError as exc:
        logger.exception("xlsx_read_failed", extra={"stage": "web"})
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "title": "Не удалось загрузить данные",
                "message": str(exc),
                "xlsx_path": settings.xlsx_path,
            },
            status_code=500,
        )

    photo_urls = {}
    for exhibit in exhibits:
        photo_url = _get_photo_url(exhibit, settings)
        if photo_url:
            photo_urls[exhibit.exhibit_id] = photo_url

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "exhibits": exhibits,
            "photo_urls": photo_urls,
            "q": q or "",
        },
    )


@router.get("/exhibits/{exhibit_id}", response_class=HTMLResponse)
def exhibit_card(request: Request, exhibit_id: int) -> HTMLResponse:
    settings = Settings()

    try:
        exhibit = with_safe_photo(get_exhibit(xlsx_path=settings.xlsx_path, exhibit_id=exhibit_id))
    except KeyError:
        return templates.TemplateResponse(
            "not_found.html",
            {"request": request, "exhibit_id": exhibit_id},
            status_code=404,
        )
    except InfraError as exc:
        logger.exception("xlsx_read_failed", extra={"stage": "web"})
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "title": "Не удалось загрузить данные",
                "message": str(exc),
                "xlsx_path": settings.xlsx_path,
            },
            status_code=500,
        )

    photo_url = _get_photo_url(exhibit, settings)

    return templates.TemplateResponse(
        "card.html",
        {"request": request, "exhibit": exhibit, "photo_url": photo_url},
    )
