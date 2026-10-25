from datetime import datetime, timezone

from jira_analytics.analytics import open_durations_days, parse_jira_datetime
from jira_analytics.models import Issue


def utc(*args) -> datetime:
    return datetime(*args, tzinfo=timezone.utc)


def test_parse_jira_datetime_parses_standard_format():
    result = parse_jira_datetime("2020-01-31T12:00:00.000+0000")
    assert result == utc(2020, 1, 31, 12, 0, 0)


def test_parse_jira_datetime_returns_none_for_empty_value():
    assert parse_jira_datetime(None) is None


def test_open_durations_days_ignores_unresolved_issues():
    issues = [
        Issue("K-1", utc(2020, 1, 1), None),
        Issue("K-2", utc(2020, 1, 1), utc(2020, 1, 3)),
    ]
    assert open_durations_days(issues) == [2.0]


def test_open_durations_days_skips_resolved_before_created():
    issues = [Issue("K-1", utc(2020, 1, 5), utc(2020, 1, 1))]
    assert open_durations_days(issues) == []