from itertools import islice

import pytest

from jira_analytics.issue_mapper import to_issue
from jira_analytics.jira_client import JiraClient

pytestmark = pytest.mark.integration


def test_real_jira_returns_closed_issues_with_history():
    client = JiraClient("https://issues.apache.org/jira", page_size=5)
    jql = "project = KAFKA AND resolution IS NOT EMPTY ORDER BY created ASC"
    raw_issues = islice(
        client.search_issues(jql, ["created", "resolutiondate"], expand="changelog"), 5
    )
    issues = [to_issue(raw) for raw in raw_issues]
    assert len(issues) == 5
    assert all(issue.resolved is not None for issue in issues)