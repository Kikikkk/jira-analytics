from datetime import datetime, date, timedelta, timezone
from itertools import accumulate
from collections import defaultdict
from collections import Counter
from .models import Issue, DailyStats, UserTaskCount

JIRA_DT_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"
SECONDS_PER_DAY = 86400
SECONDS_PER_HOUR = 3600
PRIORITY_ORDER = ("Blocker", "Critical", "Major", "Minor", "Trivial")

def parse_jira_datetime(value: str | None) -> datetime | None:
    """Разбирает дату JIRA вида 2020-01-31T12:00:00.000+0000."""
    return datetime.strptime(value, JIRA_DT_FORMAT) if value else None

def open_durations_days(issues: list[Issue]) -> list[float]:
    """Время в открытом состоянии (в днях) для закрытых задач."""
    return [
        (i.resolved - i.created).total_seconds() / SECONDS_PER_DAY
        for i in issues
        if i.resolved is not None and i.resolved >= i.created
    ]

def time_in_status_days(issues: list[Issue]) -> dict[str, list[float]]:
    """Для каждого статуса возвращает список значений (по одному на задачу):
    сколько дней закрытая задача провела в этом статусе.
    Время в последнем (терминальном) статусе не учитывается."""
    result: dict[str, list[float]] = defaultdict(list)
    for issue in issues:
        if issue.resolved is None or not issue.transitions:
            continue
        per_status: dict[str, float] = defaultdict(float)
        prev_time = issue.created
        prev_status = issue.transitions[0].from_status
        for transition in issue.transitions:
            seconds = (transition.at - prev_time).total_seconds()
            if prev_status and seconds >= 0:
                per_status[prev_status] += seconds / SECONDS_PER_DAY
            prev_time, prev_status = transition.at, transition.to_status
        for status, days in per_status.items():
            result[status].append(days)
    return dict(result)

def _to_utc_date(value: datetime) -> date:
    """Календарный день в UTC, чтобы часовые пояса не разносили даты."""
    return value.astimezone(timezone.utc).date()

def daily_created_resolved(issues: list[Issue]) -> DailyStats:
    """Количество созданных и закрытых задач по каждому дню
    (включая дни без событий) и накопительные итоги."""
    created_by_day = Counter(_to_utc_date(i.created) for i in issues)
    resolved_by_day = Counter(
        _to_utc_date(i.resolved) for i in issues if i.resolved is not None
    )
    if not created_by_day:
        return DailyStats([], [], [], [], [])

    first = min(created_by_day)
    last = max(max(created_by_day), max(resolved_by_day, default=first))
    days = [first + timedelta(days=n) for n in range((last - first).days + 1)]
    created = [created_by_day.get(d, 0) for d in days]
    resolved = [resolved_by_day.get(d, 0) for d in days]
    return DailyStats(
        days, created, resolved,
        list(accumulate(created)), list(accumulate(resolved)),
    )

def top_users(issues: list[Issue], limit: int = 30) -> list[UserTaskCount]:
    """Топ пользователей по сумме задач в ролях исполнителя и репортера.
    Сортировка по убыванию суммы, при равенстве по имени."""
    as_assignee = Counter(i.assignee for i in issues if i.assignee)
    as_reporter = Counter(i.reporter for i in issues if i.reporter)
    users = [
        UserTaskCount(name, as_assignee.get(name, 0), as_reporter.get(name, 0))
        for name in set(as_assignee) | set(as_reporter)
    ]
    users.sort(key=lambda u: (-u.total, u.name))
    return users[:limit]

def logged_time_hours(issues: list[Issue]) -> list[float]:
    """Залогированное время (в часах) для закрытых задач.
    Задачи без залогированного времени пропускаются."""
    return [
        i.time_spent_seconds / SECONDS_PER_HOUR
        for i in issues
        if i.resolved is not None and i.time_spent_seconds
    ]

def priority_counts(issues: list[Issue]) -> list[tuple[str, int]]:
    """Количество задач по уровням приоритета.
    Стандартные уровни идут в порядке серьёзности, остальные после них
    по убыванию количества. Задачи без приоритета пропускаются."""
    counts = Counter(i.priority for i in issues if i.priority)
    known = [(name, counts[name]) for name in PRIORITY_ORDER if name in counts]
    other = sorted(
        ((name, n) for name, n in counts.items() if name not in PRIORITY_ORDER),
        key=lambda pair: (-pair[1], pair[0]),
    )
    return known + other