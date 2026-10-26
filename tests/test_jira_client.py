from unittest.mock import MagicMock, patch

import pytest
import requests

from jira_analytics.jira_client import JiraClient, JiraClientError


def make_response(payload: dict) -> MagicMock:
    response = MagicMock()
    response.json.return_value = payload
    response.raise_for_status.return_value = None
    return response


def make_client(**kwargs) -> JiraClient:
    client = JiraClient("https://example.com/", **kwargs)
    client.session = MagicMock()  # сеть не используется
    return client


def test_search_issues_paginates_until_total():
    client = make_client(page_size=2)
    client.session.get.side_effect = [
        make_response({"issues": [{"key": "K-1"}, {"key": "K-2"}], "total": 3}),
        make_response({"issues": [{"key": "K-3"}], "total": 3}),
    ]
    keys = [i["key"] for i in client.search_issues("project = K", ["created"])]
    assert keys == ["K-1", "K-2", "K-3"]
    assert client.session.get.call_args_list[1].kwargs["params"]["startAt"] == 2


def test_search_issues_passes_expand_parameter():
    client = make_client()
    client.session.get.return_value = make_response({"issues": [{"key": "K-1"}], "total": 1})
    list(client.search_issues("project = K", ["created"], expand="changelog"))
    assert client.session.get.call_args.kwargs["params"]["expand"] == "changelog"


def test_search_issues_stops_on_empty_page():
    client = make_client()
    client.session.get.return_value = make_response({"issues": [], "total": 5})
    assert list(client.search_issues("project = K", ["created"])) == []


@patch("jira_analytics.jira_client.time.sleep")
def test_get_retries_after_network_error(mock_sleep):
    client = make_client(retries=3)
    client.session.get.side_effect = [
        requests.ConnectionError("network down"),
        make_response({"ok": True}),
    ]
    assert client._get("/rest/api/2/search", {}) == {"ok": True}
    assert client.session.get.call_count == 2
    mock_sleep.assert_called_once()


@patch("jira_analytics.jira_client.time.sleep")
def test_get_raises_jira_client_error_after_all_retries(mock_sleep):
    client = make_client(retries=3)
    client.session.get.side_effect = requests.ConnectionError("network down")
    with pytest.raises(JiraClientError):
        client._get("/rest/api/2/search", {})
    assert client.session.get.call_count == 3