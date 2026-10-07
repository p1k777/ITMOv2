from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional
import uuid


ISO_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


def now_iso() -> str:
    # Store timestamps in a consistent ISO format (UTC, Z)
    return datetime.utcnow().strftime(ISO_FORMAT)


@dataclass
class Task:
    id: str
    title: str
    status: str = "todo"  # todo | done
    created_at: str = field(default_factory=now_iso)
    due_date: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    @staticmethod
    def new(title: str, due_date: Optional[str] = None, tags: Optional[List[str]] = None) -> "Task":
        return Task(id=str(uuid.uuid4()), title=title, due_date=due_date, tags=tags or [])

    def to_dict(self) -> dict:
        return asdict(self)
