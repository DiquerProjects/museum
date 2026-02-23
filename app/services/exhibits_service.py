from __future__ import annotations

from dataclasses import replace
from typing import Optional

from app.services.models import Exhibit
from app.services.xlsx_repository import read_exhibits_from_xlsx


def list_exhibits(
    *,
    xlsx_path: str,
    q: Optional[str] = None,
    museum: Optional[str] = None,
    category: Optional[str] = None,
) -> list[Exhibit]:
    exhibits = read_exhibits_from_xlsx(xlsx_path=xlsx_path)

    def norm(s: str) -> str:
        return s.casefold().strip()

    if q:
        qn = norm(q)
        exhibits = [
            e
            for e in exhibits
            if qn in norm(e.name)
            or qn in norm(e.description)
            or qn in norm(e.museum)
            or qn in norm(e.category)
            or qn in norm(e.period)
        ]

    if museum:
        mn = norm(museum)
        exhibits = [e for e in exhibits if norm(e.museum) == mn]

    if category:
        cn = norm(category)
        exhibits = [e for e in exhibits if norm(e.category) == cn]

    return sorted(exhibits, key=lambda e: e.exhibit_id)


def get_exhibit(*, xlsx_path: str, exhibit_id: int) -> Exhibit:
    exhibits = read_exhibits_from_xlsx(xlsx_path=xlsx_path)
    for e in exhibits:
        if e.exhibit_id == exhibit_id:
            return e
    raise KeyError("exhibit_not_found")


def with_safe_photo(exhibit: Exhibit) -> Exhibit:
    photo = exhibit.photo_file.replace("..", "").replace("\\", "/")
    return replace(exhibit, photo_file=photo)
