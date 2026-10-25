from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class Issue:
    key: str
    created: datetime
    resolved: datetime | None