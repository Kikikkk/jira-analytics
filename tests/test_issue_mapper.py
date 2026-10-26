from jira_analytics.issue_mapper import parse_transitions, to_issue


def make_raw():
    return {
        "key": "KAFKA-1",
        "fields": {
            "created": "2020-01-01T00:00:00.000+0000",
            "resolutiondate": "2020-01-05T00:00:00.000+0000",
        },
        "changelog": {"histories": [
            {"created": "2020-01-05T00:00:00.000+0000",
             "items": [{"field": "status", "fromString": "In Progress", "toString": "Resolved"}]},
            {"created": "2020-01-02T00:00:00.000+0000",
             "items": [{"field": "assignee", "fromString": None, "toString": "bob"},
                       {"field": "status", "fromString": "Open", "toString": "In Progress"}]},
        ]},
    }


def test_parse_transitions_keeps_only_status_changes_sorted_by_time():
    transitions = parse_transitions(make_raw())
    assert [(t.from_status, t.to_status) for t in transitions] == [
        ("Open", "In Progress"), ("In Progress", "Resolved"),
    ]


def test_to_issue_without_changelog_has_no_transitions():
    raw = make_raw()
    del raw["changelog"]
    assert to_issue(raw).transitions == ()


def test_to_issue_reads_users_and_handles_unassigned():
    raw = make_raw()
    raw["fields"]["assignee"] = None
    raw["fields"]["reporter"] = {"displayName": "Alice", "name": "alice"}
    issue = to_issue(raw)
    assert issue.assignee is None
    assert issue.reporter == "Alice"


def test_to_issue_reads_time_spent():
    raw = make_raw()
    raw["fields"]["timespent"] = 3600
    assert to_issue(raw).time_spent_seconds == 3600