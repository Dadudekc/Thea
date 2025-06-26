"""Data models for Tools Database (minimal for scaffold)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

@dataclass(slots=True)
class Tool:
    id: Optional[int]
    name: str
    description: str
    code: str
    readme: Optional[str]
    added_at: Optional[str] = None 