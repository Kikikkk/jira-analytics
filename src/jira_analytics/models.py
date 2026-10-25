from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Transition:
    """Переход задачи между статусами."""
    at: datetime
    from_status: str | None
    to_status: str | None


@dataclass(frozen=True)
class Issue:
    key: str
    created: datetime
    resolved: datetime | None
    transitions: tuple[Transition, ...] = ()