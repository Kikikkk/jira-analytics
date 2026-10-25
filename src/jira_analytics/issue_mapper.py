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


def to_issue(raw: dict) -> Issue:
    """Преобразует JSON задачи из JIRA в модель Issue."""
    fields = raw["fields"]
    return Issue(
        key=raw["key"],
        created=parse_jira_datetime(fields["created"]),
        resolved=parse_jira_datetime(fields.get("resolutiondate")),
        transitions=parse_transitions(raw),
    )