from dataclasses import dataclass, field
from datetime import date
from typing import Optional, List


@dataclass
class Todo:
    title: str
    id: Optional[int] = None
    base_date: date = field(default_factory=date.today)
    tasks: List['Task'] = field(default_factory=list)
