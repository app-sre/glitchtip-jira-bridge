import pytest
from jira import JIRA
from pytest_mock import MockerFixture

from glitchtip_jira_bridge.backends.jira import create_issue
from glitchtip_jira_bridge.models import GlitchtipAlert
from glitchtip_jira_bridge.tasks import create_jira_ticket


def test_create_jira_ticket(
    mocker: MockerFixture, glitchtip_alert: GlitchtipAlert
) -> None:
    create_issue_mock = mocker.patch(
        "glitchtip_jira_bridge.tasks.create_issue", autospec=True
    )
    mocker.patch("glitchtip_jira_bridge.tasks.JIRA", autospec=True)
    mocker.patch("glitchtip_jira_bridge.tasks.boto3", autospec=True)

    create_jira_ticket(jira_project_key="TEST", alert=glitchtip_alert)

    create_issue_mock.assert_called_once_with(
        project_key="TEST",
        summary=glitchtip_alert.issue_title,
        description="issue text\n-----\nGlitchtip issue: https://glitchtip.devshift.net/app-sre/issues/12345",
        url="https://glitchtip.devshift.net/app-sre/issues/12345",
        labels=["glitchtip"] + glitchtip_alert.labels,
        jira=mocker.ANY,
        issue_cache=mocker.ANY,
        limits=mocker.ANY,
    )


def test_create_jira_ticket_retry(
    mocker: MockerFixture, glitchtip_alert: GlitchtipAlert
) -> None:
    create_issue_mock = mocker.patch(
        "glitchtip_jira_bridge.tasks.create_issue", autospec=True
    )
    create_issue_mock.side_effect = [ValueError("just a stupid exception")]
    mocker.patch("glitchtip_jira_bridge.tasks.JIRA", autospec=True)
    mocker.patch("glitchtip_jira_bridge.tasks.boto3", autospec=True)

    with pytest.raises(ValueError):
        create_jira_ticket(jira_project_key="TEST", alert=glitchtip_alert)
