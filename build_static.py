from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path
from typing import Dict, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.config.settings import Settings
from app.services.exhibits_service import list_exhibits, with_safe_photo
from app.utils.errors import InfraError


BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "app" / "api" / "templates"
STATIC_DIR = BASE_DIR / "app" / "api" / "static"


def _safe_photo_name(exhibit, photos_dir: Path) -> Optional[str]:
    candidates = [f"{exhibit.exhibit_id}{ext}" for ext in (".png", ".jpg", ".jpeg", ".webp")]
    if exhibit.photo_file:
        candidates.append(exhibit.photo_file)

    for filename in candidates:
        safe_name = filename.replace("..", "").replace("\\", "/")
        photo_fs_path = photos_dir / safe_name
        if photo_fs_path.exists():
            return safe_name
    return None


def render_static(output_dir: Path) -> None:
    settings = Settings()
    xlsx_path = (BASE_DIR / settings.xlsx_path).resolve()
    photos_dir = (BASE_DIR / settings.photos_dir).resolve()

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
    )

    try:
        exhibits = [with_safe_photo(e) for e in list_exhibits(xlsx_path=str(xlsx_path))]
    except InfraError as exc:
        raise SystemExit(f"Не удалось прочитать XLSX: {exc}") from exc

    if output_dir.exists():
        shutil.rmtree(output_dir)
    (output_dir / "exhibits").mkdir(parents=True, exist_ok=True)

    # Копируем статику и фото
    shutil.copytree(STATIC_DIR, output_dir / "static")
    if photos_dir.exists():
        shutil.copytree(photos_dir, output_dir / "photos")

    index_template = env.get_template("index.html")
    card_template = env.get_template("card.html")

    # Главная
    photo_urls_index: Dict[int, str] = {}
    for e in exhibits:
        photo_name = _safe_photo_name(e, photos_dir)
        if photo_name:
            photo_urls_index[e.exhibit_id] = f"photos/{photo_name}"

    index_html = index_template.render(
        exhibits=exhibits,
        photo_urls=photo_urls_index,
        q="",
        static_prefix="./static/",
    )
    (output_dir / "index.html").write_text(index_html, encoding="utf-8")

    # Карточки
    for e in exhibits:
        photo_name = _safe_photo_name(e, photos_dir)
        photo_url = f"../../photos/{photo_name}" if photo_name else None
        card_html = card_template.render(
            exhibit=e,
            photo_url=photo_url,
            static_prefix="../../static/",
            home_href="../../",
        )
        card_dir = output_dir / "exhibits" / str(e.exhibit_id)
        card_dir.mkdir(parents=True, exist_ok=True)
        (card_dir / "index.html").write_text(card_html, encoding="utf-8")

    print(f"Готово. Статика собрана в {output_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Сборка статичного сайта для GitHub Pages")
    parser.add_argument("--output", default="dist", help="Каталог вывода (по умолчанию dist)")
    args = parser.parse_args()
    render_static(Path(args.output).resolve())


if __name__ == "__main__":
    main()
