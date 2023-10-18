from pytest_mock import MockerFixture

from glitchtip_jira_bridge.backends.jira import create_issue
from glitchtip_jira_bridge.models import Issue


def test_create_issue_new_ticket(mocker: MockerFixture) -> None:
    jira_mock = mocker.MagicMock()
    jira_mock.search_issues.return_value = []
    issue_mock = mocker.MagicMock()
    issue_mock.key = "JIRA-123"
    issue_mock.fields.resolution = None
    jira_mock.create_issue.return_value = issue_mock
    issue_cache_mock = mocker.MagicMock()
    issue_cache_mock.get.return_value = None
    limits_mock = mocker.MagicMock()
    limits_mock.is_allowed.return_value = True

    create_issue(
        project_key="PROJECT",
        summary="summary",
        description="description",
        url="https://glitchtip.example.com/issue/123",
        labels=["label"],
        jira=jira_mock,
        issue_cache=issue_cache_mock,
        limits=limits_mock,
    )

    issue_cache_mock.get.assert_called_once_with(
        "https://glitchtip.example.com/issue/123"
    )
    jira_mock.search_issues.assert_called_once_with(
        "labels='https://glitchtip.example.com/issue/123'"
    )
    jira_mock.create_issue.assert_called_once_with(
        project="PROJECT",
        summary="summary",
        description="description",
        labels=["label", "https://glitchtip.example.com/issue/123"],
        issuetype={"name": "Bug"},
    )
    issue_cache_mock.set.assert_called_once_with(
        jira_key="JIRA-123", issue_url="https://glitchtip.example.com/issue/123"
    )
    limits_mock.is_allowed.assert_called_once_with("PROJECT")


def test_create_issue_limits_hit(mocker: MockerFixture) -> None:
    jira_mock = mocker.MagicMock()
    jira_mock.search_issues.return_value = []
    issue_mock = mocker.MagicMock()
    issue_mock.key = "JIRA-123"
    issue_mock.fields.resolution = None
    jira_mock.create_issue.return_value = issue_mock
    issue_cache_mock = mocker.MagicMock()
    issue_cache_mock.get.return_value = None
    limits_mock = mocker.MagicMock()
    limits_mock.is_allowed.return_value = False

    create_issue(
        project_key="PROJECT",
        summary="summary",
        description="description",
        url="https://glitchtip.example.com/issue/123",
        labels=["label"],
        jira=jira_mock,
        issue_cache=issue_cache_mock,
        limits=limits_mock,
    )

    issue_cache_mock.get.assert_called_once_with(
        "https://glitchtip.example.com/issue/123"
    )
    jira_mock.search_issues.assert_called_once_with(
        "labels='https://glitchtip.example.com/issue/123'"
    )
    jira_mock.create_issue.assert_not_called()
    issue_cache_mock.set.assert_not_called()
    limits_mock.is_allowed.assert_called_once_with("PROJECT")


def test_create_issue_ticket_exists_but_not_cached(mocker: MockerFixture) -> None:
    issue_mock = mocker.MagicMock()
    issue_mock.key = "JIRA-123"
    issue_mock.fields.resolution = None
    jira_mock = mocker.MagicMock()
    jira_mock.search_issues.return_value = [issue_mock]
    jira_mock.create_issue.return_value = issue_mock
    issue_cache_mock = mocker.MagicMock()
    issue_cache_mock.get.return_value = None
    limits_mock = mocker.MagicMock()
    limits_mock.is_allowed.return_value = True

    create_issue(
        project_key="PROJECT",
        summary="summary",
        description="description",
        url="https://glitchtip.example.com/issue/123",
        labels=["label"],
        jira=jira_mock,
        issue_cache=issue_cache_mock,
        limits=limits_mock,
    )

    issue_cache_mock.get.assert_called_once_with(
        "https://glitchtip.example.com/issue/123"
    )
    jira_mock.search_issues.assert_called_once_with(
        "labels='https://glitchtip.example.com/issue/123'"
    )
    jira_mock.create_issue.assert_not_called()
    issue_cache_mock.set.assert_called_once_with(
        jira_key="JIRA-123", issue_url="https://glitchtip.example.com/issue/123"
    )
    limits_mock.is_allowed.assert_not_called()


def test_create_issue_ticket_already_cached(mocker: MockerFixture) -> None:
    issue_mock = mocker.MagicMock()
    issue_mock.key = "JIRA-123"
    issue_mock.fields.resolution = None
    jira_mock = mocker.MagicMock()
    jira_mock.search_issues.return_value = [issue_mock]
    jira_mock.create_issue.return_value = issue_mock
    issue_cache_mock = mocker.MagicMock()
    issue_cache_mock.get.return_value = Issue(
        jira_key="JIRA-123",
        glitchtip_issue_url="https://glitchtip.example.com/issue/123",
    )
    limits_mock = mocker.MagicMock()
    limits_mock.is_allowed.return_value = True

    create_issue(
        project_key="PROJECT",
        summary="summary",
        description="description",
        url="https://glitchtip.example.com/issue/123",
        labels=["label"],
        jira=jira_mock,
        issue_cache=issue_cache_mock,
        limits=limits_mock,
    )

    issue_cache_mock.get.assert_called_once_with(
        "https://glitchtip.example.com/issue/123"
    )
    jira_mock.search_issues.assert_not_called()
    jira_mock.create_issue.assert_not_called()
    issue_cache_mock.set.assert_not_called()
    limits_mock.is_allowed.assert_not_called()


def test_create_issue_ticket_reopen(mocker: MockerFixture) -> None:
    issue_mock = mocker.MagicMock()
    issue_mock.key = "JIRA-123"
    issue_mock.fields.resolution = object()
    jira_mock = mocker.MagicMock()
    jira_mock.search_issues.return_value = [issue_mock]
    jira_mock.create_issue.return_value = issue_mock
    jira_mock.transitions.return_value = [{"id": "1"}]
    issue_cache_mock = mocker.MagicMock()
    issue_cache_mock.get.return_value = None
    limits_mock = mocker.MagicMock()
    limits_mock.is_allowed.return_value = True

    create_issue(
        project_key="PROJECT",
        summary="summary",
        description="description",
        url="https://glitchtip.example.com/issue/123",
        labels=["label"],
        jira=jira_mock,
        issue_cache=issue_cache_mock,
        limits=limits_mock,
    )

    issue_cache_mock.get.assert_called_once_with(
        "https://glitchtip.example.com/issue/123"
    )
    jira_mock.search_issues.assert_called_once_with(
        "labels='https://glitchtip.example.com/issue/123'"
    )
    jira_mock.create_issue.assert_not_called()
    jira_mock.transition_issue.assert_called_once_with(issue_mock, "1")
    issue_cache_mock.set.assert_called_once_with(
        jira_key="JIRA-123", issue_url="https://glitchtip.example.com/issue/123"
    )
    limits_mock.is_allowed.assert_not_called()
