from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class Todo:
    title: str
    id: Optional[int] = None
    base_date: date = field(default_factory=date.today)
