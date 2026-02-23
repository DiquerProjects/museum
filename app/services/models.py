from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class Exhibit:
    exhibit_id: int
    name: str
    museum: str
    description: str
    period: str
    category: str
    received_date: Optional[date]
    photo_file: str
    voronezh_story: str
