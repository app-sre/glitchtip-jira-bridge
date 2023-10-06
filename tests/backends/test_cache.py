from pytest_mock import MockerFixture

from glitchtip_jira_bridge.backends.cache import (
    Cache,
    IssueCache,
)
from glitchtip_jira_bridge.models import Issue


def test_cache_get(mocker: MockerFixture) -> None:
    dyn_resource_mock = mocker.MagicMock()
    cache = Cache(dyn_resource_mock, "table_name")
    cache.table.get_item.side_effect = [{"Item": {"v": "value"}}, {}]

    assert cache.get("pk") == "value"
    assert cache.get("pk") is None


def test_cache_set(mocker: MockerFixture) -> None:
    dyn_resource_mock = mocker.MagicMock()
    cache = Cache(dyn_resource_mock, "table_name")
    cache.table.put_item.side_effect = [None]

    cache.set("pk", "value", 1234)

    cache.table.put_item.assert_called_once_with(
        Item={
            "key": "pk",
            "v": "value",
            "ttl": 1234,
        }
    )


def test_issue_cache_get(mocker: MockerFixture) -> None:
    cache_backend_mock = mocker.MagicMock()
    cache_backend_mock.get.side_effect = ["JIRA-123", None]
    issue_cache = IssueCache(cache_backend_mock, 10)

    assert issue_cache.get("https://glitchtip.example.com/issue/123") == Issue(
        jira_key="JIRA-123",
        glitchtip_issue_url="https://glitchtip.example.com/issue/123",
    )
    assert issue_cache.get("https://glitchtip.example.com/issue/not-cached") is None


def test_issue_cache_set(mocker: MockerFixture) -> None:
    time_mock = mocker.patch("glitchtip_jira_bridge.backends.cache.time")
    time_mock.time.return_value = 1234
    cache_backend_mock = mocker.MagicMock()
    issue_cache = IssueCache(cache_backend_mock, 10)

    issue_cache.set("JIRA-123", "https://glitchtip.example.com/issue/123")

    cache_backend_mock.set.assert_called_once_with(
        pk="https://glitchtip.example.com/issue/123", value="JIRA-123", ttl=1234 + 10
    )
