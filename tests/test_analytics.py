from datetime import datetime, timezone

from jira_analytics.analytics import (open_durations_days, parse_jira_datetime,
                                      time_in_status_days, daily_created_resolved,
                                      top_users, logged_time_hours, priority_counts)
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


def test_top_users_counts_both_roles():
    issues = [
        Issue("K-1", utc(2020, 1, 1), None, assignee="Bob", reporter="Alice"),
        Issue("K-2", utc(2020, 1, 1), None, assignee="Bob", reporter="Bob"),
    ]
    users = top_users(issues)
    assert (users[0].name, users[0].assignee, users[0].reporter) == ("Bob", 2, 1)
    assert (users[1].name, users[1].assignee, users[1].reporter) == ("Alice", 0, 1)


def test_top_users_respects_limit_and_sorts_by_total():
    issues = [
        Issue(f"K-{n}", utc(2020, 1, 1), None, assignee=f"user{n % 3}")
        for n in range(7)
    ]
    users = top_users(issues, limit=2)
    assert [u.name for u in users] == ["user0", "user1"]


def test_top_users_ignores_unassigned():
    issues = [Issue("K-1", utc(2020, 1, 1), None)]
    assert top_users(issues) == []


def test_logged_time_hours_converts_seconds_to_hours():
    issues = [Issue("K-1", utc(2020, 1, 1), utc(2020, 1, 2), time_spent_seconds=7200)]
    assert logged_time_hours(issues) == [2.0]


def test_logged_time_hours_skips_issues_without_logged_time():
    issues = [
        Issue("K-1", utc(2020, 1, 1), utc(2020, 1, 2)),
        Issue("K-2", utc(2020, 1, 1), utc(2020, 1, 2), time_spent_seconds=0),
    ]
    assert logged_time_hours(issues) == []


def test_logged_time_hours_ignores_unresolved_issues():
    issues = [Issue("K-1", utc(2020, 1, 1), None, time_spent_seconds=3600)]
    assert logged_time_hours(issues) == []


def test_priority_counts_orders_by_severity():
    issues = [
        Issue("K-1", utc(2020, 1, 1), None, priority="Minor"),
        Issue("K-2", utc(2020, 1, 1), None, priority="Blocker"),
        Issue("K-3", utc(2020, 1, 1), None, priority="Minor"),
    ]
    assert priority_counts(issues) == [("Blocker", 1), ("Minor", 2)]


def test_priority_counts_puts_unknown_levels_last():
    issues = [
        Issue("K-1", utc(2020, 1, 1), None, priority="Urgent"),
        Issue("K-2", utc(2020, 1, 1), None, priority="Major"),
    ]
    assert priority_counts(issues) == [("Major", 1), ("Urgent", 1)]


def test_priority_counts_skips_issues_without_priority():
    issues = [Issue("K-1", utc(2020, 1, 1), None)]
    assert priority_counts(issues) == []