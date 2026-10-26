from dataclasses import dataclass
from datetime import datetime, date


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
    assignee: str | None = None
    reporter: str | None = None
    time_spent_seconds: int | None = None


@dataclass(frozen=True)
class DailyStats:
    """Статистика по дням: списки одинаковой длины, по одному значению на день."""
    days: list[date]
    created: list[int]
    resolved: list[int]
    created_cumulative: list[int]
    resolved_cumulative: list[int]


@dataclass(frozen=True)
class UserTaskCount:
    """Количество задач пользователя в ролях исполнителя и репортера."""
    name: str
    assignee: int
    reporter: int

    @property
    def total(self) -> int:
        return self.assignee + self.reporter