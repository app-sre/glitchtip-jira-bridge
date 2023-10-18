import pytest
from pytest_mock import MockerFixture

from glitchtip_jira_bridge.models import Attachment
from glitchtip_jira_bridge.tasks import create_jira_ticket


def test_create_jira_ticket(mocker: MockerFixture, issue: Attachment) -> None:
    create_issue_mock = mocker.patch(
        "glitchtip_jira_bridge.tasks.create_issue", autospec=True
    )
    mocker.patch("glitchtip_jira_bridge.tasks.JIRA", autospec=True)
    mocker.patch("glitchtip_jira_bridge.tasks.boto3", autospec=True)

    create_jira_ticket(jira_project_key="TEST", issue=issue)

    create_issue_mock.assert_called_once_with(
        project_key="TEST",
        summary=issue.title,
        description="issue text\n-----\nGlitchtip issue: https://glitchtip.devshift.net/app-sre/issues/12345",
        url="https://glitchtip.devshift.net/app-sre/issues/12345",
        labels=["glitchtip"] + issue.labels,
        jira=mocker.ANY,
        issue_cache=mocker.ANY,
        limits=mocker.ANY,
    )


def test_create_jira_ticket_retry(mocker: MockerFixture, issue: Attachment) -> None:
    create_issue_mock = mocker.patch(
        "glitchtip_jira_bridge.tasks.create_issue", autospec=True
    )
    create_issue_mock.side_effect = [ValueError("just a stupid exception")]
    mocker.patch("glitchtip_jira_bridge.tasks.JIRA", autospec=True)
    mocker.patch("glitchtip_jira_bridge.tasks.boto3", autospec=True)

    with pytest.raises(ValueError):
        create_jira_ticket(jira_project_key="TEST", issue=issue)
