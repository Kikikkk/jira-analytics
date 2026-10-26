from .analytics import parse_jira_datetime
from .models import Issue, Transition


def parse_transitions(raw: dict) -> tuple[Transition, ...]:
    """Извлекает переходы между статусами из changelog, по возрастанию времени."""
    histories = raw.get("changelog", {}).get("histories", [])
    transitions = [
        Transition(
            at=parse_jira_datetime(history["created"]),
            from_status=item.get("fromString"),
            to_status=item.get("toString"),
        )
        for history in histories
        for item in history.get("items", [])
        if item.get("field") == "status"
    ]
    return tuple(sorted(transitions, key=lambda t: t.at))

def _user_name(value: dict | None) -> str | None:
    """Имя пользователя из поля assignee/reporter (может быть null)."""
    if not value:
        return None
    return value.get("displayName") or value.get("name")


def to_issue(raw: dict) -> Issue:
    """Преобразует JSON задачи из JIRA в модель Issue."""
    fields = raw["fields"]
    return Issue(
        key=raw["key"],
        created=parse_jira_datetime(fields["created"]),
        resolved=parse_jira_datetime(fields.get("resolutiondate")),
        transitions=parse_transitions(raw),
        assignee=_user_name(fields.get("assignee")),
        reporter=_user_name(fields.get("reporter")),
        time_spent_seconds=fields.get("timespent"),
        priority=(fields.get("priority") or {}).get("name"),
    )