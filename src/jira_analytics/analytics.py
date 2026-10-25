from datetime import datetime
from .models import Issue

JIRA_DT_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"

def parse_jira_datetime(value: str | None) -> datetime | None:
    """Разбирает дату JIRA вида 2020-01-31T12:00:00.000+0000."""
    return datetime.strptime(value, JIRA_DT_FORMAT) if value else None

def open_durations_days(issues: list[Issue]) -> list[float]:
    """Время в открытом состоянии (в днях) для закрытых задач."""
    return [
        (i.resolved - i.created).total_seconds() / 86400
        for i in issues
        if i.resolved is not None and i.resolved >= i.created
    ]