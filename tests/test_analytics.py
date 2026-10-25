from datetime import datetime, timezone

from jira_analytics.analytics import (open_durations_days, parse_jira_datetime,
                                      time_in_status_days, daily_created_resolved)
from jira_analytics.models import Issue
from jira_analytics.models import Transition

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

def test_time_in_status_days_sums_time_per_status():
    issue = Issue(
        "K-1", utc(2020, 1, 1), utc(2020, 1, 5),
        transitions=(
            Transition(utc(2020, 1, 2), "Open", "In Progress"),
            Transition(utc(2020, 1, 5), "In Progress", "Resolved"),
        ),
    )
    assert time_in_status_days([issue]) == {"Open": [1.0], "In Progress": [3.0]}


def test_time_in_status_days_sums_repeated_visits():
    issue = Issue(
        "K-1", utc(2020, 1, 1), utc(2020, 1, 5),
        transitions=(
            Transition(utc(2020, 1, 2), "Open", "In Progress"),
            Transition(utc(2020, 1, 3), "In Progress", "Open"),
            Transition(utc(2020, 1, 5), "Open", "Closed"),
        ),
    )
    result = time_in_status_days([issue])
    assert result["Open"] == [3.0]
    assert result["In Progress"] == [1.0]


def test_time_in_status_days_ignores_unresolved_issues():
    issue = Issue(
        "K-1", utc(2020, 1, 1), None,
        transitions=(Transition(utc(2020, 1, 2), "Open", "In Progress"),),
    )
    assert time_in_status_days([issue]) == {}


def test_daily_created_resolved_counts_and_cumulative():
    issues = [
        Issue("K-1", utc(2020, 1, 1), utc(2020, 1, 3)),
        Issue("K-2", utc(2020, 1, 1), None),
    ]
    stats = daily_created_resolved(issues)
    assert [d.day for d in stats.days] == [1, 2, 3]
    assert stats.created == [2, 0, 0]
    assert stats.resolved == [0, 0, 1]
    assert stats.created_cumulative == [2, 2, 2]
    assert stats.resolved_cumulative == [0, 0, 1]


def test_daily_created_resolved_empty_input():
    assert daily_created_resolved([]).days == []